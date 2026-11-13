"""Complaints / disputes."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.bookings.models import Booking, BookingStatusHistory
from apps.notifications.services import notify
from .forms import ComplaintForm
from .models import Complaint


@login_required
def create_complaint(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('customer__user', 'provider__user'), id=booking_id
    )

    is_cust = (
        hasattr(request.user, 'customer_profile')
        and booking.customer_id == request.user.customer_profile.id
    )
    is_prov = (
        hasattr(request.user, 'provider_profile')
        and booking.provider_id == request.user.provider_profile.id
    )
    if not (is_cust or is_prov or request.user.is_admin_user):
        messages.error(request, "You are not authorised to lodge a complaint for this booking.")
        return redirect('core:home')

    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                complaint = form.save(commit=False)
                complaint.booking = booking
                complaint.raised_by = request.user
                complaint.status = 'OPEN'
                complaint.save()

                if booking.status in ('IN_PROGRESS', 'WORK_PROOF_SUBMITTED'):
                    previous = booking.status
                    booking.status = 'DISPUTED'
                    booking.save(update_fields=['status', 'updated_at'])
                    BookingStatusHistory.objects.create(
                        booking=booking,
                        from_status=previous,
                        to_status='DISPUTED',
                        changed_by=request.user,
                        notes=f"Dispute ticket {complaint.complaint_number} raised.",
                    )

                from apps.accounts.models import User
                for admin_user in (
                    User.objects.filter(role='ADMIN') | User.objects.filter(is_staff=True)
                ).distinct():
                    notify(
                        admin_user,
                        f"New dispute {complaint.complaint_number}",
                        f"{request.user.get_full_name() or request.user.email} raised "
                        f"'{complaint.get_category_display()}' on booking "
                        f"{booking.booking_number}.",
                        'SYSTEM',
                        f"/admin-panel/complaints/{complaint.id}/resolve/",
                    )

            messages.success(
                request,
                f"Ticket {complaint.complaint_number} logged. Support will review it within 24 hours.",
            )
            return redirect('complaints:detail', complaint_id=complaint.id)
        messages.error(request, "Please correct the highlighted fields.")
    else:
        form = ComplaintForm()

    return render(request, 'complaints/create.html', {
        'booking': booking,
        'form': form,
        'title': f'Report an Issue — Booking #{booking.booking_number}',
    })


@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(raised_by=request.user).select_related('booking')
    paginator = Paginator(complaints.order_by('-created_at'), 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'complaints/list.html', {
        'complaints': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'title': 'My Support Tickets',
    })


@login_required
def complaint_detail(request, complaint_id):
    complaint = get_object_or_404(
        Complaint.objects.select_related('booking', 'raised_by'), id=complaint_id
    )
    if complaint.raised_by != request.user and not request.user.is_admin_user:
        messages.error(request, "Access denied.")
        return redirect('core:home')

    return render(request, 'complaints/detail.html', {
        'complaint': complaint,
        'title': f'Ticket {complaint.complaint_number}',
    })
