"""Technician portal: jobs, status flow, work proof, earnings, KYC."""
import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.decorators import provider_required
from apps.bookings.models import Booking, BookingStatusHistory, WorkProof
from apps.notifications.services import notify
from apps.payments.models import EarningsLedger, PayoutRequest
from .forms import (
    ProviderProfileEditForm,
    ProviderSkillForm,
    ProviderUserEditForm,
    VerificationDocumentForm,
)
from .models import ProviderProfile, ProviderSkill, VerificationDocument

logger = logging.getLogger('homebuddy.professionals')

PAGE_SIZE = 10
VALID_TRANSITIONS = {
    'ACCEPTED': ['EN_ROUTE'],
    'EN_ROUTE': ['ARRIVED'],
    'ARRIVED': ['IN_PROGRESS'],
}


@login_required
@provider_required
def dashboard(request):
    profile, _ = ProviderProfile.objects.get_or_create(user=request.user)

    incoming_requests = Booking.objects.filter(
        provider=profile, status='REQUESTED'
    ).select_related('service', 'customer__user', 'address').order_by('-created_at')

    active_jobs = Booking.objects.filter(
        provider=profile,
        status__in=['ACCEPTED', 'EN_ROUTE', 'ARRIVED', 'IN_PROGRESS'],
    ).select_related('service', 'customer__user').order_by('scheduled_date')

    recent_completed = Booking.objects.filter(
        provider=profile, status='COMPLETED'
    ).select_related('service').order_by('-updated_at')[:5]

    ledger = EarningsLedger.objects.filter(provider=profile)
    totals = ledger.aggregate(
        gross=Sum('gross_amount'),
        commission=Sum('commission_amount'),
        net=Sum('net_earnings'),
        unpaid=Sum('net_earnings', filter=models_q_unpaid()),
    )

    return render(request, 'professional/dashboard.html', {
        'profile': profile,
        'incoming_requests': incoming_requests,
        'active_jobs': active_jobs,
        'recent_completed': recent_completed,
        'total_earned': totals['net'] or Decimal('0.00'),
        'pending_payout': totals['unpaid'] or Decimal('0.00'),
        'verification_docs': VerificationDocument.objects.filter(provider=profile),
        'title': 'Provider Dashboard',
    })


def models_q_unpaid():
    from django.db.models import Q
    return Q(is_paid_out=False)


@login_required
@provider_required
def edit_profile(request):
    profile, _ = ProviderProfile.objects.get_or_create(user=request.user)
    skills = ProviderSkill.objects.filter(provider=profile)
    u_form = ProviderUserEditForm(instance=request.user)
    p_form = ProviderProfileEditForm(instance=profile)
    s_form = ProviderSkillForm()

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            u_form = ProviderUserEditForm(request.POST, request.FILES, instance=request.user)
            p_form = ProviderProfileEditForm(request.POST, instance=profile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, "Professional profile updated.")
                return redirect('professionals:edit_profile')
            messages.error(request, "Please correct the highlighted fields.")
        elif 'add_skill' in request.POST:
            s_form = ProviderSkillForm(request.POST)
            if s_form.is_valid():
                skill = s_form.save(commit=False)
                skill.provider = profile
                skill.save()
                messages.success(request, f"Skill '{skill.skill_name}' added.")
                return redirect('professionals:edit_profile')
            messages.error(request, "Please correct the skill details.")
        elif 'toggle_availability' in request.POST:
            profile.is_available_today = not profile.is_available_today
            profile.save(update_fields=['is_available_today', 'updated_at'])
            state = "available" if profile.is_available_today else "unavailable"
            messages.info(request, f"You are now marked {state} for new jobs today.")
            return redirect('professionals:edit_profile')

    return render(request, 'professional/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        's_form': s_form,
        'profile': profile,
        'skills': skills,
        'title': 'Edit Professional Profile',
    })


@login_required
@provider_required
def verification_view(request):
    profile, _ = ProviderProfile.objects.get_or_create(user=request.user)
    documents = VerificationDocument.objects.filter(provider=profile)

    if request.method == 'POST':
        form = VerificationDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.provider = profile
            doc.status = 'PENDING'
            doc.save()

            staff = _admin_users()
            for admin_user in staff:
                notify(
                    admin_user,
                    "New KYC document submitted",
                    f"{profile.business_name or profile.user.get_full_name()} uploaded "
                    f"{doc.get_document_type_display()} for review.",
                    'VERIFICATION',
                    '/admin-panel/verifications/',
                )
            messages.success(request, f"{doc.get_document_type_display()} uploaded for review.")
            return redirect('professionals:verification')
        messages.error(request, "Upload failed. Check the file type and size (max 5 MB).")
    else:
        form = VerificationDocumentForm()

    return render(request, 'professional/verification.html', {
        'profile': profile,
        'documents': documents,
        'form': form,
        'title': 'Identity Verification (KYC)',
    })


def _admin_users():
    from apps.accounts.models import User
    return User.objects.filter(role='ADMIN') | User.objects.filter(is_staff=True)


@login_required
@provider_required
def jobs_view(request):
    profile, _ = ProviderProfile.objects.get_or_create(user=request.user)
    status_filter = (request.GET.get('status') or '').strip()

    jobs = Booking.objects.filter(provider=profile).select_related(
        'service', 'customer__user', 'address'
    )
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    jobs = jobs.order_by('-created_at')

    paginator = Paginator(jobs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'professional/jobs.html', {
        'profile': profile,
        'jobs': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'querystring': query_params.urlencode(),
        'selected_status': status_filter,
        'title': 'My Service Jobs',
    })


@login_required
@provider_required
@require_POST
def accept_booking(request, booking_id):
    profile = get_object_or_404(ProviderProfile, user=request.user)
    booking = get_object_or_404(Booking, id=booking_id, provider=profile, status='REQUESTED')

    with transaction.atomic():
        booking.status = 'ACCEPTED'
        booking.save(update_fields=['status', 'updated_at'])
        BookingStatusHistory.objects.create(
            booking=booking,
            from_status='REQUESTED',
            to_status='ACCEPTED',
            changed_by=request.user,
            notes="Provider accepted the booking request.",
        )
        notify(
            booking.customer.user,
            "Technician accepted your booking",
            f"{profile.business_name or profile.user.get_full_name()} accepted booking "
            f"{booking.booking_number} for {booking.scheduled_date:%d %b %Y}.",
            'BOOKING',
            f"/bookings/{booking.id}/",
        )

    messages.success(request, f"Booking #{booking.booking_number} accepted.")
    return redirect('professionals:jobs')


@login_required
@provider_required
@require_POST
def reject_booking(request, booking_id):
    profile = get_object_or_404(ProviderProfile, user=request.user)
    booking = get_object_or_404(Booking, id=booking_id, provider=profile, status='REQUESTED')

    reason = (request.POST.get('rejection_reason') or '').strip() or "Technician unavailable"

    with transaction.atomic():
        booking.status = 'REJECTED'
        booking.rejection_reason = reason[:500]
        booking.save(update_fields=['status', 'rejection_reason', 'updated_at'])
        BookingStatusHistory.objects.create(
            booking=booking,
            from_status='REQUESTED',
            to_status='REJECTED',
            changed_by=request.user,
            notes=f"Declined: {reason}",
        )
        notify(
            booking.customer.user,
            "Technician declined your booking",
            f"Booking {booking.booking_number} was declined ({reason}). "
            "Please choose another technician or time slot.",
            'BOOKING',
            f"/bookings/{booking.id}/",
        )

    messages.info(request, f"Booking #{booking.booking_number} declined.")
    return redirect('professionals:jobs')


@login_required
@provider_required
@require_POST
def update_job_status(request, booking_id, new_status):
    profile = get_object_or_404(ProviderProfile, user=request.user)
    booking = get_object_or_404(Booking, id=booking_id, provider=profile)

    if new_status not in VALID_TRANSITIONS.get(booking.status, []):
        messages.error(
            request,
            f"Cannot move from {booking.get_status_display()} to {new_status.replace('_', ' ').title()}.",
        )
        return redirect('professionals:jobs')

    with transaction.atomic():
        old_status = booking.status
        booking.status = new_status
        booking.save(update_fields=['status', 'updated_at'])
        BookingStatusHistory.objects.create(
            booking=booking,
            from_status=old_status,
            to_status=new_status,
            changed_by=request.user,
            notes=f"Provider updated status to {new_status.replace('_', ' ').title()}",
        )
        notify(
            booking.customer.user,
            f"Booking update: {booking.get_status_display()}",
            f"Your technician moved booking {booking.booking_number} to "
            f"'{booking.get_status_display()}'.",
            'BOOKING',
            f"/bookings/{booking.id}/",
        )

    messages.success(request, f"Status updated to {booking.get_status_display()}.")
    return redirect('professionals:jobs')


@login_required
@provider_required
def work_proof_upload(request, booking_id):
    profile = get_object_or_404(ProviderProfile, user=request.user)
    booking = get_object_or_404(Booking, id=booking_id, provider=profile)

    if booking.status not in ('IN_PROGRESS', 'WORK_PROOF_SUBMITTED'):
        messages.error(request, "Start the job before uploading work proof.")
        return redirect('bookings:detail', booking_id=booking.id)

    proof, _ = WorkProof.objects.get_or_create(booking=booking)

    if request.method == 'POST':
        before_photo = request.FILES.get('before_photo')
        after_photo = request.FILES.get('after_photo')
        work_notes = (request.POST.get('work_notes') or '').strip()

        if before_photo:
            proof.before_photo = before_photo
        if after_photo:
            proof.after_photo = after_photo
        if work_notes:
            proof.work_notes = work_notes

        if proof.before_photo and proof.after_photo and proof.work_notes:
            with transaction.atomic():
                proof.submitted_at = timezone.now()
                proof.save()

                old_status = booking.status
                booking.status = 'WORK_PROOF_SUBMITTED'
                booking.save(update_fields=['status', 'updated_at'])
                BookingStatusHistory.objects.create(
                    booking=booking,
                    from_status=old_status,
                    to_status='WORK_PROOF_SUBMITTED',
                    changed_by=request.user,
                    notes="Work proof photos and notes submitted. Awaiting customer sign-off.",
                )
                notify(
                    booking.customer.user,
                    "Work proof ready for your approval",
                    f"{profile.business_name or 'Your technician'} submitted before/after photos "
                    f"for booking {booking.booking_number}. Please review and confirm.",
                    'BOOKING',
                    f"/bookings/{booking.id}/confirm/",
                )
            messages.success(request, "Work proof submitted for customer sign-off.")
            return redirect('professionals:jobs')

        messages.error(request, "Before photo, after photo and work notes are all required.")

    return render(request, 'professional/work_proof.html', {
        'booking': booking,
        'proof': proof,
        'title': f'Submit Work Proof — {booking.booking_number}',
    })


@login_required
@provider_required
def earnings_view(request):
    profile = get_object_or_404(ProviderProfile, user=request.user)
    ledger = EarningsLedger.objects.filter(provider=profile).select_related('booking')
    totals = ledger.aggregate(
        gross=Sum('gross_amount'),
        commission=Sum('commission_amount'),
        net=Sum('net_earnings'),
        unpaid=Sum('net_earnings', filter=models_q_unpaid()),
    )

    available_balance = totals['unpaid'] or Decimal('0.00')

    if request.method == 'POST':
        amount_raw = (request.POST.get('amount') or '').strip()
        bank_name = (request.POST.get('bank_account_name') or '').strip()
        account_no = (request.POST.get('bank_account_number') or '').strip()
        ifsc = (request.POST.get('bank_ifsc') or '').strip().upper()

        if not all([amount_raw, bank_name, account_no, ifsc]):
            messages.error(request, "All payout fields are required.")
        else:
            try:
                req_amount = Decimal(amount_raw)
            except InvalidOperation:
                messages.error(request, "Enter a valid payout amount.")
                return redirect('professionals:earnings')

            minimum = Decimal(settings.MIN_PAYOUT_AMOUNT)
            pending = PayoutRequest.objects.filter(
                provider=profile, status__in=['REQUESTED', 'APPROVED']
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            if req_amount < minimum:
                messages.error(request, f"Minimum payout is ₹{minimum}.")
            elif req_amount > (available_balance - pending):
                messages.error(
                    request,
                    f"Amount exceeds your available balance (₹{available_balance - pending}).",
                )
            else:
                PayoutRequest.objects.create(
                    provider=profile,
                    amount=req_amount,
                    bank_account_name=bank_name[:100],
                    bank_account_number=account_no[:30],
                    bank_ifsc=ifsc[:20],
                )
                for admin_user in _admin_users():
                    notify(
                        admin_user,
                        "New payout request",
                        f"{profile.business_name or profile.user.get_full_name()} requested "
                        f"a payout of ₹{req_amount}.",
                        'PAYMENT',
                        '/admin-panel/payouts/',
                    )
                messages.success(request, f"Payout request for ₹{req_amount} submitted.")
                return redirect('professionals:earnings')

    return render(request, 'professional/earnings.html', {
        'profile': profile,
        'ledger_entries': ledger.order_by('-created_at')[:50],
        'gross_total': totals['gross'] or Decimal('0.00'),
        'commission_total': totals['commission'] or Decimal('0.00'),
        'net_total': totals['net'] or Decimal('0.00'),
        'available_balance': available_balance,
        'payout_requests': PayoutRequest.objects.filter(provider=profile).order_by('-requested_at'),
        'min_payout': Decimal(settings.MIN_PAYOUT_AMOUNT),
        'title': 'Earnings & Financial Ledger',
    })


def public_profile_view(request, provider_id):
    provider = get_object_or_404(
        ProviderProfile.objects.select_related('user'), id=provider_id
    )
    from apps.reviews.models import Review

    return render(request, 'professional/public_profile.html', {
        'provider': provider,
        'skills': ProviderSkill.objects.filter(provider=provider),
        'reviews': Review.objects.filter(
            provider=provider, is_approved=True
        ).select_related('customer__user').order_by('-created_at')[:20],
        'title': f'{provider.business_name or provider.user.get_full_name()} — HomeBuddy',
    })
