"""Reviews: one per completed booking, drives provider ratings."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import customer_required
from apps.bookings.models import Booking
from apps.notifications.services import notify
from .forms import ReviewForm


@login_required
@customer_required
def create_review(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('provider__user', 'service'),
        id=booking_id, customer__user=request.user,
    )

    if booking.status != 'COMPLETED':
        messages.error(request, "Reviews can only be submitted after service completion.")
        return redirect('bookings:detail', booking_id=booking.id)

    if hasattr(booking, 'review'):
        messages.info(request, "You have already reviewed this booking.")
        return redirect('bookings:detail', booking_id=booking.id)

    if not booking.provider:
        messages.error(request, "No technician was assigned to this booking.")
        return redirect('bookings:detail', booking_id=booking.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                review = form.save(commit=False)
                review.booking = booking
                review.customer = booking.customer
                review.provider = booking.provider
                review.save()
                review.provider.update_rating()

                notify(
                    booking.provider.user,
                    f"New {review.rating}★ review",
                    f"A customer reviewed your work on booking {booking.booking_number}.",
                    'SYSTEM',
                    f"/provider/{booking.provider.id}/",
                )
            messages.success(
                request,
                f"Thank you for reviewing {booking.provider.business_name or 'your technician'}!",
            )
            return redirect('bookings:detail', booking_id=booking.id)
        messages.error(request, "Please choose a rating and write your review.")
    else:
        form = ReviewForm()

    return render(request, 'reviews/create.html', {
        'booking': booking,
        'form': form,
        'title': f'Review Service — {booking.service.name}',
    })
