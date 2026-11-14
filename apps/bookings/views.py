"""Booking engine: creation, tracking, completion sign-off, cancellation."""
import datetime
import json
import logging
import math
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.decorators import customer_required
from apps.customers.models import Address, CustomerProfile
from apps.notifications.services import notify
from apps.payments.models import EarningsLedger, Invoice, Payment
from apps.professionals.models import ProviderProfile
from apps.services.models import Service
from .forms import BookingCreationForm
from .models import Booking, BookingStatusHistory, WorkProof, LocationUpdate

logger = logging.getLogger('homebuddy.bookings')

ACTIVE_STATUSES = [
    'REQUESTED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED',
    'IN_PROGRESS', 'WORK_PROOF_SUBMITTED',
]


def pick_provider(service, address):
    """
    Auto-assignment: verified + available + actually covers this pincode,
    preferring providers who explicitly offer the service.

    Falls back to any verified provider covering the pincode, and only then to
    any verified provider, so a booking is never silently left unassigned.
    """
    pincode = (address.pincode or '').strip() if address else ''

    explicit = (
        ProviderProfile.objects
        .filter(is_verified=True, is_available_today=True,
                provided_services__service=service, provided_services__is_active=True)
        .select_related('user')
        .order_by('-avg_rating', 'total_jobs_completed')
    )
    if pincode:
        for candidate in explicit:
            if pincode in _pincode_set(candidate):
                return candidate
    else:
        first = explicit.first()
        if first:
            return first

    if pincode:
        for candidate in ProviderProfile.objects.filter(
            is_verified=True, is_available_today=True
        ).select_related('user').order_by('-avg_rating'):
            if pincode in _pincode_set(candidate):
                return candidate

    return ProviderProfile.objects.filter(
        is_verified=True, is_available_today=True
    ).order_by('-avg_rating').first()


def _pincode_set(provider):
    raw = provider.service_pincodes or ''
    return {part.strip() for part in raw.replace(';', ',').split(',') if part.strip()}


def has_slot_conflict(provider, scheduled_date, time_slot, exclude_booking_id=None):
    """True when the provider already has a live job in that slot."""
    if provider is None:
        return False
    qs = Booking.objects.filter(
        provider=provider,
        scheduled_date=scheduled_date,
        time_slot=time_slot,
        status__in=ACTIVE_STATUSES,
    )
    if exclude_booking_id:
        qs = qs.exclude(id=exclude_booking_id)
    return qs.exists()


@login_required
@customer_required
def create_booking(request, service_slug):
    service = get_object_or_404(Service, slug=service_slug, is_active=True)
    customer_profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = BookingCreationForm(
            request.POST, user=request.user, service=service
        )
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = customer_profile
            booking.service = service
            booking.service_price = service.base_price

            # Resolve delivery address: use chosen saved address OR create from inline fields
            selected_address = form.cleaned_data.get('address')
            if not selected_address:
                house = (form.cleaned_data.get('house_flat_no') or '').strip()
                street = (form.cleaned_data.get('street') or '').strip()
                addr1 = f"{house}, {street}".strip(', ') if street else house
                addr2 = (form.cleaned_data.get('area') or '').strip()
                city = (form.cleaned_data.get('city') or 'Pune').strip() or 'Pune'
                state = (form.cleaned_data.get('state') or 'Maharashtra').strip() or 'Maharashtra'
                pincode = (form.cleaned_data.get('pincode') or '').strip()
                title = form.cleaned_data.get('address_title') or 'Home'
                is_default = form.cleaned_data.get('save_as_default', True)

                selected_address = Address.objects.create(
                    user=request.user,
                    title=title,
                    address_line1=addr1,
                    address_line2=addr2,
                    landmark=street if street != house else '',
                    city=city,
                    state=state,
                    pincode=pincode,
                    latitude=Decimal('18.520400'),
                    longitude=Decimal('73.856700'),
                    is_default=is_default,
                )

            booking.address = selected_address

            # Save customer contact info to User profile if not yet populated
            cust_name = (form.cleaned_data.get('customer_name') or '').strip()
            cust_phone = (form.cleaned_data.get('customer_phone') or '').strip()
            phone_digits = ''.join(ch for ch in cust_phone if ch.isdigit())
            user_dirty = False
            if phone_digits and len(phone_digits) == 10 and not request.user.phone:
                request.user.phone = phone_digits
                user_dirty = True
            if cust_name and not request.user.first_name:
                parts = cust_name.split(maxsplit=1)
                request.user.first_name = parts[0]
                if len(parts) > 1:
                    request.user.last_name = parts[1]
                user_dirty = True
            if user_dirty:
                request.user.save()

            wants_emergency = booking.is_emergency
            if wants_emergency and not service.is_emergency_eligible:
                form.add_error(
                    'is_emergency',
                    "Emergency express dispatch is not available for this service.",
                )
                messages.error(
                    request,
                    "This service is not eligible for emergency express dispatch.",
                )
                return _render_booking_form(request, service, form)

            booking.is_emergency = wants_emergency and service.is_emergency_eligible
            booking.emergency_fee = (
                service.emergency_surcharge if booking.is_emergency else Decimal('0.00')
            )

            if booking.is_emergency:
                booking.scheduled_date = timezone.localdate()

            booking.calculate_total()

            if not booking.provider:
                booking.provider = pick_provider(service, booking.address)

            if booking.provider and has_slot_conflict(
                booking.provider, booking.scheduled_date, booking.time_slot
            ):
                # Try to find somebody else free in that slot before failing.
                original = booking.provider
                for candidate in ProviderProfile.objects.filter(
                    is_verified=True, is_available_today=True
                ).exclude(id=original.id).order_by('-avg_rating'):
                    if not has_slot_conflict(candidate, booking.scheduled_date, booking.time_slot):
                        booking.provider = candidate
                        break
                else:
                    form.add_error(
                        'time_slot',
                        "The selected technician is already booked in this slot. "
                        "Please pick another time slot.",
                    )
                    messages.error(request, "That time slot is no longer available.")
                    return _render_booking_form(request, service, form)

            with transaction.atomic():
                booking.status = 'REQUESTED'
                booking.save()
                BookingStatusHistory.objects.create(
                    booking=booking,
                    from_status=None,
                    to_status='REQUESTED',
                    changed_by=request.user,
                    notes="Customer created the booking.",
                )
                Payment.objects.get_or_create(
                    booking=booking,
                    defaults={
                        'amount': booking.total_amount,
                        'status': 'PENDING',
                        'payment_method': 'ONLINE_RAZORPAY',
                    },
                )
                notify(
                    request.user,
                    "Booking created",
                    f"Your booking {booking.booking_number} for {service.name} has been created. "
                    "Complete the payment step to confirm your slot.",
                    'BOOKING',
                    f"/bookings/{booking.id}/",
                )
                if booking.provider:
                    notify(
                        booking.provider.user,
                        "New job request",
                        f"You have a new {service.name} job on "
                        f"{booking.scheduled_date:%d %b %Y} ({booking.time_slot}).",
                        'BOOKING',
                        f"/bookings/{booking.id}/",
                    )

            messages.success(
                request,
                f"Booking #{booking.booking_number} created. Choose your payment method.",
            )
            # Proceed directly to Step 3: Payment — NEVER TO LOGIN!
            return redirect('payments:checkout', booking_id=booking.id)
        else:
            messages.error(request, "Please correct the highlighted errors.")
    else:
        initial = {}
        if request.GET.get('emergency') == '1' and service.is_emergency_eligible:
            initial['is_emergency'] = True
            initial['scheduled_date'] = datetime.date.today().isoformat()
        form = BookingCreationForm(user=request.user, service=service, initial=initial)

    return _render_booking_form(request, service, form)


def _render_booking_form(request, service, form):
    saved_addresses = (
        Address.objects.filter(user=request.user)
        if request.user.is_authenticated
        else Address.objects.none()
    )
    return render(request, 'bookings/book.html', {
        'service': service,
        'form': form,
        'saved_addresses': saved_addresses,
        'title': f'Book {service.name}',
    })


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related(
            'customer__user', 'provider__user', 'service', 'address'
        ),
        id=booking_id,
    )

    is_cust = (
        hasattr(request.user, 'customer_profile')
        and booking.customer_id == request.user.customer_profile.id
    )
    is_prov = (
        hasattr(request.user, 'provider_profile')
        and booking.provider_id == request.user.provider_profile.id
    )
    is_adm = request.user.is_admin_user or request.user.is_superuser

    if not (is_cust or is_prov or is_adm):
        messages.error(request, "Access denied. You are not authorised to view this booking.")
        return redirect('core:home')

    latest_location = booking.location_updates.first()
    cust_lat = float((booking.address.latitude if booking.address else None) or Decimal('18.5204'))
    cust_lng = float((booking.address.longitude if booking.address else None) or Decimal('73.8567'))

    return render(request, 'bookings/tracking.html', {
        'booking': booking,
        'history': booking.status_history.select_related('changed_by'),
        'proof': getattr(booking, 'work_proof', None),
        'payment': getattr(booking, 'payment', None),
        'invoice': getattr(booking, 'invoice', None),
        'review': getattr(booking, 'review', None),
        'latest_location': latest_location,
        'cust_lat': cust_lat,
        'cust_lng': cust_lng,
        'is_customer': is_cust,
        'is_provider': is_prov,
        'is_admin': is_adm,
        'title': f'Booking #{booking.booking_number}',
    })


@login_required
@customer_required
def confirm_completion(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('provider', 'customer__user'),
        id=booking_id, customer__user=request.user,
    )
    proof = get_object_or_404(WorkProof, booking=booking)

    if booking.status != 'WORK_PROOF_SUBMITTED':
        messages.info(
            request,
            "This booking is not awaiting your sign-off right now.",
        )
        return redirect('bookings:detail', booking_id=booking.id)

    if request.method == 'POST':
        feedback = request.POST.get('feedback', '').strip()
        commission_rate = Decimal(settings.PLATFORM_COMMISSION_RATE)

        with transaction.atomic():
            proof.customer_confirmed = True
            proof.customer_confirmed_at = timezone.now()
            proof.customer_feedback = feedback
            proof.save(update_fields=[
                'customer_confirmed', 'customer_confirmed_at', 'customer_feedback',
            ])

            old_status = booking.status
            booking.status = 'COMPLETED'
            booking.save(update_fields=['status', 'updated_at'])

            BookingStatusHistory.objects.create(
                booking=booking,
                from_status=old_status,
                to_status='COMPLETED',
                changed_by=request.user,
                notes=f"Customer confirmed completion. Feedback: {feedback or 'Satisfied'}",
            )

            if booking.provider:
                ProviderProfile.objects.filter(pk=booking.provider_id).update(
                    total_jobs_completed=booking.provider.total_jobs_completed + 1
                )
                commission_amount = (
                    booking.total_amount * (commission_rate / Decimal('100.00'))
                ).quantize(Decimal('0.01'))
                EarningsLedger.objects.get_or_create(
                    booking=booking,
                    defaults={
                        'provider': booking.provider,
                        'gross_amount': booking.total_amount,
                        'commission_rate': commission_rate,
                        'commission_amount': commission_amount,
                        'net_earnings': booking.total_amount - commission_amount,
                    },
                )

            Invoice.objects.get_or_create(
                booking=booking,
                defaults={
                    'invoice_number': f"INV-{booking.booking_number.replace('HB-', '')}",
                    'subtotal': booking.service_price,
                    'total_amount': booking.total_amount,
                },
            )

            notify(
                request.user,
                "Service completed",
                f"Booking {booking.booking_number} is complete. "
                "Your invoice is available in the booking page.",
                'BOOKING',
                f"/bookings/{booking.id}/",
            )
            if booking.provider:
                notify(
                    booking.provider.user,
                    "Job signed off",
                    f"Customer confirmed completion of {booking.booking_number}. "
                    f"₹{booking.total_amount - (booking.total_amount * commission_rate / Decimal('100'))} "
                    "has been added to your ledger.",
                    'BOOKING',
                    f"/bookings/{booking.id}/",
                )

        messages.success(
            request,
            "Service completed! Please rate your technician.",
        )
        return redirect('reviews:create', booking_id=booking.id)

    return render(request, 'bookings/confirm_completion.html', {
        'booking': booking,
        'proof': proof,
        'title': f'Confirm Service Completion — #{booking.booking_number}',
    })


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    is_cust = (
        hasattr(request.user, 'customer_profile')
        and booking.customer_id == request.user.customer_profile.id
    )
    is_prov = (
        hasattr(request.user, 'provider_profile')
        and booking.provider_id == request.user.provider_profile.id
    )
    if not (is_cust or is_prov or request.user.is_admin_user):
        messages.error(request, "You are not authorised to cancel this booking.")
        return redirect('core:home')

    if request.method != 'POST':
        messages.error(request, "Cancellations must be submitted from the booking page.")
        return redirect('bookings:detail', booking_id=booking.id)

    if booking.status in ('COMPLETED', 'CANCELLED'):
        messages.error(request, "This booking is already finalised.")
        return redirect('bookings:detail', booking_id=booking.id)

    reason = (request.POST.get('cancellation_reason') or '').strip() or "Cancelled by user"

    with transaction.atomic():
        old_status = booking.status
        booking.status = 'CANCELLED'
        booking.cancellation_reason = reason[:500]
        booking.save(update_fields=['status', 'cancellation_reason', 'updated_at'])

        BookingStatusHistory.objects.create(
            booking=booking,
            from_status=old_status,
            to_status='CANCELLED',
            changed_by=request.user,
            notes=f"Cancelled: {reason}",
        )

        notify(
            request.user,
            "Booking cancelled",
            f"Booking {booking.booking_number} was cancelled. Reason: {reason}",
            'BOOKING',
            f"/bookings/{booking.id}/",
        )
        if booking.provider:
            notify(
                booking.provider.user,
                "Job cancelled",
                f"Booking {booking.booking_number} was cancelled by the customer.",
                'BOOKING',
                f"/bookings/{booking.id}/",
            )

    payment = getattr(booking, 'payment', None)
    if payment and payment.status == 'SUCCESS' and not payment.is_demo:
        messages.warning(
            request,
            "This booking was already paid. A refund must be issued from the admin "
            "payments panel — please raise a support ticket.",
        )

    messages.info(request, f"Booking #{booking.booking_number} has been cancelled.")
    return redirect('bookings:detail', booking_id=booking.id)


@login_required
def emergency_booking_view(request):
    """Shows services eligible for 45-minute express dispatch."""
    services = (
        Service.objects.filter(is_emergency_eligible=True, is_active=True)
        .select_related('category')
        .order_by('category__name', 'base_price')
    )
    available_today = ProviderProfile.objects.filter(
        is_verified=True, is_available_today=True
    ).count()

    return render(request, 'bookings/emergency.html', {
        'services': services,
        'available_today': available_today,
        'title': 'Emergency Express Dispatch',
    })


@login_required
@customer_required
def rebook(request, booking_id):
    """Clone a past booking into a new request (same service + address)."""
    previous = get_object_or_404(
        Booking, id=booking_id, customer__user=request.user
    )
    messages.info(
        request,
        "Pick a date and slot to rebook the same service at the same address.",
    )
    return redirect('bookings:create', service_slug=previous.service.slug)


def _haversine_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


@login_required
def update_location(request, booking_id):
    """
    POST-only endpoint: assigned provider reports live GPS coordinates.
    Only permitted during active booking stages (ACCEPTED, EN_ROUTE, ARRIVED, IN_PROGRESS).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    booking = get_object_or_404(Booking, id=booking_id)

    # Authorization check: only assigned provider can report location
    if not (hasattr(request.user, 'provider_profile') and booking.provider_id == request.user.provider_profile.id):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if booking.status not in ['ACCEPTED', 'EN_ROUTE', 'ARRIVED', 'IN_PROGRESS']:
        return JsonResponse({'error': 'Location tracking is only active during scheduled service delivery'}, status=400)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST
        lat = Decimal(str(data.get('latitude')))
        lng = Decimal(str(data.get('longitude')))
        heading = Decimal(str(data.get('heading'))) if data.get('heading') is not None else None
        speed = Decimal(str(data.get('speed'))) if data.get('speed') is not None else None
    except (ValueError, TypeError, InvalidOperation):
        return JsonResponse({'error': 'Invalid coordinates provided'}, status=400)

    loc = LocationUpdate.objects.create(
        booking=booking,
        provider=booking.provider,
        latitude=lat,
        longitude=lng,
        heading=heading,
        speed=speed,
    )
    return JsonResponse({'status': 'ok', 'timestamp': loc.timestamp.isoformat()})


@login_required
def get_live_location(request, booking_id):
    """
    JSON endpoint: provides real-time technician coordinates, customer address pin,
    and computed ETA for map rendering.
    """
    booking = get_object_or_404(
        Booking.objects.select_related('customer__user', 'provider__user', 'address'),
        id=booking_id
    )

    is_cust = hasattr(request.user, 'customer_profile') and booking.customer_id == request.user.customer_profile.id
    is_prov = hasattr(request.user, 'provider_profile') and booking.provider_id == request.user.provider_profile.id
    is_adm = request.user.is_admin_user or request.user.is_superuser

    if not (is_cust or is_prov or is_adm):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    latest = booking.location_updates.first()
    cust_lat = float((booking.address.latitude if booking.address else None) or Decimal('18.5204'))
    cust_lng = float((booking.address.longitude if booking.address else None) or Decimal('73.8567'))

    if not latest or booking.status not in ['EN_ROUTE', 'ARRIVED', 'IN_PROGRESS']:
        return JsonResponse({
            'available': False,
            'status': booking.status,
            'status_display': booking.get_status_display(),
            'customer_lat': cust_lat,
            'customer_lng': cust_lng,
            'message': 'Live tracking will activate once the technician is en route.'
        })

    prov_lat = float(latest.latitude)
    prov_lng = float(latest.longitude)
    dist_km = _haversine_distance_km(prov_lat, prov_lng, cust_lat, cust_lng)

    speed = float(latest.speed) if latest.speed and float(latest.speed) > 5 else 25.0
    eta_mins = max(1, round((dist_km / speed) * 60))

    if booking.status == 'ARRIVED':
        eta_text = "Technician arrived at location"
    elif booking.status == 'IN_PROGRESS':
        eta_text = "Service in progress"
    elif dist_km < 0.2:
        eta_text = "Arriving now (< 2 mins)"
    else:
        eta_text = f"~{eta_mins} mins ({dist_km} km away)"

    return JsonResponse({
        'available': True,
        'status': booking.status,
        'status_display': booking.get_status_display(),
        'provider_lat': prov_lat,
        'provider_lng': prov_lng,
        'customer_lat': cust_lat,
        'customer_lng': cust_lng,
        'distance_km': dist_km,
        'eta_minutes': eta_mins,
        'eta_text': eta_text,
        'updated_at': latest.timestamp.isoformat(),
    })

