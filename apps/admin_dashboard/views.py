"""Custom operations dashboard (complements Django admin)."""
import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.decorators import admin_required
from apps.accounts.models import User
from apps.bookings.models import Booking, BookingStatusHistory
from apps.complaints.models import Complaint
from apps.notifications.services import notify
from apps.payments import razorpay_service
from apps.payments.models import EarningsLedger, Invoice, Payment, PayoutRequest
from apps.professionals.models import ProviderProfile, VerificationDocument
from apps.services.models import Service, Category
from apps.services.forms import ServiceForm, CategoryForm

logger = logging.getLogger('homebuddy.admin_dashboard')

PAGE_SIZE = 20
ACTIVE_STATUSES = [
    'REQUESTED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED',
    'IN_PROGRESS', 'WORK_PROOF_SUBMITTED',
]


@login_required
@admin_required
def index(request):
    booking_counts = Booking.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(status__in=ACTIVE_STATUSES)),
        completed=Count('id', filter=Q(status='COMPLETED')),
        cancelled=Count('id', filter=Q(status='CANCELLED')),
        disputed=Count('id', filter=Q(status='DISPUTED')),
    )

    revenue = Payment.objects.filter(status='SUCCESS').aggregate(
        online=Sum('amount', filter=Q(payment_method='ONLINE_RAZORPAY')),
        cash=Sum('amount', filter=Q(payment_method='CASH')),
        total=Sum('amount'),
    )
    commission = EarningsLedger.objects.aggregate(total=Sum('commission_amount'))['total']
    unpaid_earnings = EarningsLedger.objects.filter(is_paid_out=False).aggregate(
        total=Sum('net_earnings')
    )['total']

    return render(request, 'admin_dashboard/index.html', {
        'total_users': User.objects.count(),
        'total_customers': User.objects.filter(role='CUSTOMER').count(),
        'total_providers': ProviderProfile.objects.count(),
        'verified_providers': ProviderProfile.objects.filter(is_verified=True).count(),
        'pending_kyc': VerificationDocument.objects.filter(status='PENDING').count(),
        'total_bookings': booking_counts['total'],
        'active_bookings': booking_counts['active'],
        'completed_bookings': booking_counts['completed'],
        'cancelled_bookings': booking_counts['cancelled'],
        'disputed_bookings': booking_counts['disputed'],
        'total_revenue': revenue['total'] or Decimal('0.00'),
        'online_revenue': revenue['online'] or Decimal('0.00'),
        'cash_revenue': revenue['cash'] or Decimal('0.00'),
        'platform_earnings': commission or Decimal('0.00'),
        'unpaid_earnings': unpaid_earnings or Decimal('0.00'),
        'open_complaints': Complaint.objects.filter(
            status__in=['OPEN', 'INVESTIGATING']
        ).count(),
        'pending_payouts': PayoutRequest.objects.filter(status='REQUESTED').count(),
        'recent_bookings': Booking.objects.select_related(
            'customer__user', 'service', 'provider'
        ).order_by('-created_at')[:8],
        'recent_kyc': VerificationDocument.objects.filter(
            status='PENDING'
        ).select_related('provider__user')[:5],
        'demo_mode': razorpay_service.is_demo_mode(),
        'title': 'Admin Command Center',
    })


@login_required
@admin_required
def users_list(request):
    role_filter = (request.GET.get('role') or '').strip()
    search = (request.GET.get('q') or '').strip()

    users = User.objects.all().order_by('-date_joined')
    if role_filter:
        users = users.filter(role=role_filter)
    if search:
        users = users.filter(
            Q(email__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(phone__icontains=search)
        )

    paginator = Paginator(users, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'admin_dashboard/users.html', {
        'users': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'querystring': query_params.urlencode(),
        'selected_role': role_filter,
        'search': search,
        'title': 'User Management',
    })


@login_required
@admin_required
@require_POST
def toggle_user_active(request, user_id):
    """POST-only: suspending an account must never happen on a GET."""
    target = get_object_or_404(User, id=user_id)

    if target == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('admin_dashboard:users')

    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, "Only a superuser can modify another superuser.")
        return redirect('admin_dashboard:users')

    target.is_active = not target.is_active
    target.save(update_fields=['is_active'])

    state = "reactivated" if target.is_active else "suspended"
    logger.info("Admin %s %s user %s", request.user.email, state, target.email)
    messages.info(request, f"User {target.email} has been {state}.")

    if not target.is_active:
        notify(
            target,
            "Account suspended",
            "Your HomeBuddy account has been suspended. Contact support if you believe "
            "this is a mistake.",
            'SYSTEM',
        )

    return redirect('admin_dashboard:users')


@login_required
@admin_required
def verifications_list(request):
    status_filter = (request.GET.get('status') or 'PENDING').strip()
    documents = VerificationDocument.objects.select_related(
        'provider__user'
    )
    if status_filter and status_filter != 'ALL':
        documents = documents.filter(status=status_filter)
    documents = documents.order_by('-submitted_at')

    paginator = Paginator(documents, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin_dashboard/verifications.html', {
        'documents': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'selected_status': status_filter,
        'title': 'KYC Verification Queue',
    })


@login_required
@admin_required
@require_POST
def process_verification(request, doc_id, action):
    """
    Approve/reject a KYC document.

    A provider only earns the Verified badge once at least one identity document
    (Aadhaar / PAN / licence) is approved — not from a skill certificate alone.
    """
    doc = get_object_or_404(VerificationDocument.objects.select_related('provider__user'), id=doc_id)
    notes = (request.POST.get('admin_notes') or '').strip()

    if action not in ('approve', 'reject'):
        messages.error(request, "Unknown verification action.")
        return redirect('admin_dashboard:verifications')

    with transaction.atomic():
        if action == 'approve':
            doc.status = 'APPROVED'
            doc.admin_notes = notes or "Verified by admin."
            doc.reviewed_at = timezone.now()
            doc.save(update_fields=['status', 'admin_notes', 'reviewed_at'])

            identity_types = ('AADHAAR', 'PAN', 'DRIVING_LICENSE')
            has_identity = VerificationDocument.objects.filter(
                provider=doc.provider,
                status='APPROVED',
                document_type__in=identity_types,
            ).exists()

            if has_identity and not doc.provider.is_verified:
                doc.provider.is_verified = True
                doc.provider.verification_date = timezone.now()
                doc.provider.save(update_fields=['is_verified', 'verification_date'])

            notify(
                doc.provider.user,
                "KYC document approved",
                f"Your {doc.get_document_type_display()} was approved."
                + (
                    " You now carry the Verified badge."
                    if doc.provider.is_verified else
                    " Upload an identity document (Aadhaar/PAN/Licence) to earn the Verified badge."
                ),
                'VERIFICATION',
                '/provider/verification/',
            )
            messages.success(request, f"{doc.get_document_type_display()} approved.")

        else:
            doc.status = 'REJECTED'
            doc.admin_notes = notes or "Document rejected. Please re-upload a clearer copy."
            doc.reviewed_at = timezone.now()
            doc.save(update_fields=['status', 'admin_notes', 'reviewed_at'])

            notify(
                doc.provider.user,
                "KYC document rejected",
                f"Your {doc.get_document_type_display()} was rejected: {doc.admin_notes}",
                'VERIFICATION',
                '/provider/verification/',
            )
            messages.warning(request, f"{doc.get_document_type_display()} rejected.")

    return redirect('admin_dashboard:verifications')


@login_required
@admin_required
def bookings_list(request):
    status_filter = (request.GET.get('status') or '').strip()
    search = (request.GET.get('q') or '').strip()

    bookings = Booking.objects.select_related(
        'customer__user', 'provider__user', 'service'
    ).order_by('-created_at')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if search:
        bookings = bookings.filter(
            Q(booking_number__icontains=search)
            | Q(customer__user__email__icontains=search)
            | Q(provider__business_name__icontains=search)
        )

    paginator = Paginator(bookings, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'admin_dashboard/bookings.html', {
        'bookings': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'querystring': query_params.urlencode(),
        'selected_status': status_filter,
        'search': search,
        'title': 'All Bookings Oversight',
    })


@login_required
@admin_required
def complaints_list(request):
    status_filter = (request.GET.get('status') or '').strip()
    complaints = Complaint.objects.select_related(
        'booking__customer__user', 'raised_by'
    ).order_by('-created_at')
    if status_filter:
        complaints = complaints.filter(status=status_filter)

    paginator = Paginator(complaints, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin_dashboard/complaints.html', {
        'complaints': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'selected_status': status_filter,
        'title': 'Customer Dispute Resolution',
    })


@login_required
@admin_required
def resolve_complaint(request, complaint_id):
    complaint = get_object_or_404(
        Complaint.objects.select_related('booking', 'raised_by'), id=complaint_id
    )

    if request.method == 'POST':
        resolution = (request.POST.get('admin_resolution') or '').strip()
        new_status = request.POST.get('status', 'RESOLVED')

        if len(resolution) < 10:
            messages.error(request, "Please write a resolution note of at least 10 characters.")
        else:
            with transaction.atomic():
                complaint.admin_resolution = resolution
                complaint.status = new_status
                complaint.save(update_fields=['admin_resolution', 'status', 'updated_at'])

                booking = complaint.booking
                if booking.status == 'DISPUTED' and new_status in ('RESOLVED', 'CLOSED'):
                    booking.status = 'COMPLETED'
                    booking.save(update_fields=['status', 'updated_at'])
                    BookingStatusHistory.objects.create(
                        booking=booking,
                        from_status='DISPUTED',
                        to_status='COMPLETED',
                        changed_by=request.user,
                        notes=f"Dispute {complaint.complaint_number} resolved by support.",
                    )

                notify(
                    complaint.raised_by,
                    f"Support ticket {complaint.complaint_number} updated",
                    f"Status: {complaint.get_status_display()}. {resolution}",
                    'SYSTEM',
                    f"/complaints/{complaint.id}/",
                )

            messages.success(request, f"Ticket #{complaint.complaint_number} set to {new_status}.")
            return redirect('admin_dashboard:complaints')

    return render(request, 'admin_dashboard/resolve_complaint.html', {
        'complaint': complaint,
        'title': f'Resolve Dispute #{complaint.complaint_number}',
    })


@login_required
@admin_required
def payments_list(request):
    status_filter = (request.GET.get('status') or '').strip()
    method_filter = (request.GET.get('method') or '').strip()

    payments = Payment.objects.select_related('booking__customer__user').order_by('-created_at')
    if status_filter:
        payments = payments.filter(status=status_filter)
    if method_filter:
        payments = payments.filter(payment_method=method_filter)

    paginator = Paginator(payments, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'admin_dashboard/payments.html', {
        'payments': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'querystring': query_params.urlencode(),
        'selected_status': status_filter,
        'selected_method': method_filter,
        'demo_mode': razorpay_service.is_demo_mode(),
        'title': 'Payments & Refunds',
    })


@login_required
@admin_required
@require_POST
def refund_payment(request, payment_id):
    """
    Issue a full refund through Razorpay (or mark it refunded in demo mode).

    Only successful, non-cash payments can be refunded.
    """
    payment = get_object_or_404(Payment.objects.select_related('booking'), id=payment_id)

    if payment.status != 'SUCCESS':
        messages.error(request, "Only successful payments can be refunded.")
        return redirect('admin_dashboard:payments')

    if payment.payment_method == 'CASH':
        messages.error(request, "Cash payments must be refunded in person.")
        return redirect('admin_dashboard:payments')

    try:
        refund = razorpay_service.create_refund(payment.razorpay_payment_id)
    except razorpay_service.RazorpayError as exc:
        logger.exception("Refund failed for payment %s", payment_id)
        messages.error(request, f"Refund failed: {exc}")
        return redirect('admin_dashboard:payments')

    with transaction.atomic():
        payment.status = 'REFUNDED'
        payment.razorpay_refund_id = (refund or {}).get('id', '')[:100]
        payment.save(update_fields=['status', 'razorpay_refund_id', 'updated_at'])

        payment.booking.status = 'CANCELLED'
        payment.booking.save(update_fields=['status', 'updated_at'])

        EarningsLedger.objects.filter(booking=payment.booking, is_paid_out=False).delete()

        notify(
            payment.booking.customer.user,
            "Refund processed",
            f"₹{payment.amount} for booking {payment.booking.booking_number} has been refunded.",
            'PAYMENT',
            f"/bookings/{payment.booking.id}/",
        )

    messages.success(request, f"₹{payment.amount} refunded.")
    return redirect('admin_dashboard:payments')


@login_required
@admin_required
def payouts_list(request):
    status_filter = (request.GET.get('status') or '').strip()
    payouts = PayoutRequest.objects.select_related('provider__user').order_by('-requested_at')
    if status_filter:
        payouts = payouts.filter(status=status_filter)

    paginator = Paginator(payouts, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin_dashboard/payouts.html', {
        'payouts': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'selected_status': status_filter,
        'title': 'Technician Payouts',
    })


@login_required
@admin_required
@require_POST
def process_payout(request, payout_id, action):
    """Approve / reject / mark transferred a payout request."""
    payout = get_object_or_404(PayoutRequest.objects.select_related('provider__user'), id=payout_id)
    reference = (request.POST.get('admin_reference') or '').strip()

    if action not in ('approve', 'reject', 'transfer'):
        messages.error(request, "Unknown payout action.")
        return redirect('admin_dashboard:payouts')

    if action == 'approve' and payout.status != 'REQUESTED':
        messages.error(request, "Only requested payouts can be approved.")
        return redirect('admin_dashboard:payouts')

    if action == 'transfer' and payout.status != 'APPROVED':
        messages.error(request, "Approve the payout before marking it transferred.")
        return redirect('admin_dashboard:payouts')

    with transaction.atomic():
        if action == 'approve':
            payout.status = 'APPROVED'
            payout.processed_at = timezone.now()
            message = f"Payout #{payout.id} approved."
        elif action == 'reject':
            payout.status = 'REJECTED'
            payout.admin_notes = reference or "Rejected by finance admin."
            payout.processed_at = timezone.now()
            message = f"Payout #{payout.id} rejected."
        else:
            payout.status = 'TRANSFERRED'
            payout.admin_reference = reference[:100]
            payout.processed_at = timezone.now()
            EarningsLedger.objects.filter(
                provider=payout.provider, is_paid_out=False
            ).update(is_paid_out=True)
            message = f"Payout #{payout.id} transferred and ledger settled."

        payout.save()

    notify(
        payout.provider.user,
        f"Payout {payout.get_status_display()}",
        f"Your payout request of ₹{payout.amount} is now '{payout.get_status_display()}'.",
        'PAYMENT',
        '/provider/earnings/',
    )
    messages.success(request, message)
    return redirect('admin_dashboard:payouts')


@login_required
@admin_required
def services_list(request):
    category_slug = (request.GET.get('category') or '').strip()
    search = (request.GET.get('q') or '').strip()

    services = Service.objects.select_related('category').order_by('category__display_order', 'base_price')
    if category_slug:
        services = services.filter(category__slug=category_slug)
    if search:
        services = services.filter(
            Q(name__icontains=search) | Q(short_description__icontains=search) | Q(category__name__icontains=search)
        )

    categories = Category.objects.all().order_by('display_order', 'name')
    paginator = Paginator(services, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'admin_dashboard/services.html', {
        'services': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'search': search,
        'is_paginated': page_obj.has_other_pages(),
        'querystring': query_params.urlencode(),
        'title': 'Service Catalog Management',
    })


@login_required
@admin_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            messages.success(request, f"Service '{service.name}' created successfully.")
            return redirect('admin_dashboard:services')
        messages.error(request, "Please correct the highlighted errors.")
    else:
        form = ServiceForm()

    return render(request, 'admin_dashboard/service_form.html', {
        'form': form,
        'action_title': 'Add New Service',
        'title': 'Add New Service',
    })


@login_required
@admin_required
def service_edit(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f"Service '{service.name}' updated successfully.")
            return redirect('admin_dashboard:services')
        messages.error(request, "Please correct the highlighted errors.")
    else:
        form = ServiceForm(instance=service)

    return render(request, 'admin_dashboard/service_form.html', {
        'form': form,
        'service': service,
        'action_title': f'Edit Service: {service.name}',
        'title': f'Edit Service - {service.name}',
    })


@login_required
@admin_required
@require_POST
def service_delete(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if service.bookings.exists():
        service.is_active = False
        service.save(update_fields=['is_active'])
        messages.info(request, f"Service '{service.name}' has existing booking records and has been deactivated instead of deleted.")
    else:
        service.delete()
        messages.success(request, f"Service '{service.name}' removed from catalog.")
    return redirect('admin_dashboard:services')

