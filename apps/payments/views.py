"""Payments: checkout, Razorpay order creation, verified callback, cash, invoices."""
import json
import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.bookings.models import Booking, BookingStatusHistory
from apps.notifications.services import notify
from . import razorpay_service
from .models import Invoice, Payment

logger = logging.getLogger('homebuddy.payments')


def _can_access_payment(user, booking):
    """Customer who owns the booking, its provider, or platform staff."""
    if user.is_authenticated and (user.is_admin_user or user.is_staff):
        return True
    if hasattr(user, 'customer_profile') and booking.customer_id == user.customer_profile.id:
        return True
    if hasattr(user, 'provider_profile') and booking.provider_id == user.provider_profile.id:
        return True
    return False


@login_required
def checkout_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if not _can_access_payment(request.user, booking):
        messages.error(request, "You are not authorised to pay for this booking.")
        return redirect('core:home')

    if booking.status in ('CANCELLED', 'COMPLETED'):
        messages.info(request, "This booking is already closed.")
        return redirect('bookings:detail', booking_id=booking.id)

    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={'amount': booking.total_amount, 'status': 'PENDING'},
    )

    if payment.amount != booking.total_amount:
        payment.amount = booking.total_amount
        payment.save(update_fields=['amount', 'updated_at'])

    order = razorpay_service.create_order(payment)

    return render(request, 'payments/checkout.html', {
        'booking': booking,
        'payment': payment,
        'razorpay_key_id': order['key_id'],
        'razorpay_order_id': order['order_id'],
        'amount_in_paise': order['amount'],
        'currency': order['currency'],
        'demo_mode': order['demo'],
        'title': f'Checkout — Booking #{booking.booking_number}',
    })


@login_required
@require_POST
def create_order_ajax(request, booking_id):
    """
    Returns the Razorpay order payload as JSON so Checkout.js can open
    without a full page reload.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    if not _can_access_payment(request.user, booking):
        return JsonResponse({'error': 'Not authorised for this booking.'}, status=403)

    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={'amount': booking.total_amount, 'status': 'PENDING'},
    )

    try:
        order = razorpay_service.create_order(payment)
    except razorpay_service.RazorpayError as exc:
        logger.exception("Order creation failed for booking %s", booking.booking_number)
        return JsonResponse({'error': str(exc)}, status=502)

    return JsonResponse({
        'order_id': order['order_id'],
        'amount': order['amount'],
        'currency': order['currency'],
        'key_id': order['key_id'],
        'demo': order['demo'],
        'booking_number': booking.booking_number,
        'customer_name': request.user.get_full_name() or request.user.username,
        'customer_email': request.user.email,
        'customer_phone': request.user.phone or '',
    })


@login_required
@require_POST
def razorpay_callback(request, booking_id):
    """
    Server-side confirmation.

    * Live mode: the signature is verified with the Razorpay SDK. An invalid
      signature marks the payment FAILED and never confirms the booking.
    * Demo mode: an explicitly simulated payment is recorded with is_demo=True.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    if not _can_access_payment(request.user, booking):
        messages.error(request, "You are not authorised to confirm this payment.")
        return redirect('core:home')

    payment = get_object_or_404(Payment, booking=booking)

    razorpay_payment_id = (request.POST.get('razorpay_payment_id') or '').strip()
    razorpay_order_id = (request.POST.get('razorpay_order_id') or '').strip()
    razorpay_signature = (request.POST.get('razorpay_signature') or '').strip()
    demo_confirm = request.POST.get('demo_confirm') == '1'

    # ---------------------------------------------------------------- demo path
    if razorpay_service.is_demo_mode():
        if not demo_confirm:
            messages.error(
                request,
                "Demo payments must be confirmed from the checkout page. "
                "Configure Razorpay keys in .env to accept real payments.",
            )
            return redirect('payments:checkout', booking_id=booking.id)

        with transaction.atomic():
            payment.payment_method = 'ONLINE_RAZORPAY'
            payment.status = 'SUCCESS'
            payment.is_demo = True
            payment.razorpay_payment_id = razorpay_payment_id or f"pay_demo_{booking.booking_number}"
            payment.razorpay_order_id = razorpay_order_id or payment.razorpay_order_id
            payment.razorpay_signature = ''
            payment.paid_at = timezone.now()
            payment.gateway_response = {'mode': 'demo', 'simulated': True}
            payment.save()

            BookingStatusHistory.objects.create(
                booking=booking,
                from_status=booking.status,
                to_status=booking.status,
                changed_by=request.user,
                notes=(
                    f"DEMO payment of ₹{payment.amount} recorded (no real money moved). "
                    f"Ref: {payment.razorpay_payment_id}"
                ),
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
                "Demo payment recorded",
                f"Booking {booking.booking_number}: a simulated payment of ₹{payment.amount} "
                f"was recorded. No real money was charged.",
                'PAYMENT',
                f"/bookings/{booking.id}/",
            )

        messages.warning(
            request,
            f"Demo payment of ₹{payment.amount} recorded — no real money was charged. "
            "Add Razorpay keys in .env to enable live payments.",
        )
        return redirect('bookings:detail', booking_id=booking.id)

    # ---------------------------------------------------------------- live path
    try:
        razorpay_service.verify_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        )
    except razorpay_service.PaymentVerificationError as exc:
        with transaction.atomic():
            payment.status = 'FAILED'
            payment.failure_reason = str(exc)[:255]
            payment.razorpay_payment_id = razorpay_payment_id or None
            payment.save(update_fields=[
                'status', 'failure_reason', 'razorpay_payment_id', 'updated_at',
            ])
        logger.error("Payment verification failed for booking %s", booking.booking_number)
        messages.error(
            request,
            "We could not verify that payment with Razorpay, so it has not been "
            "recorded. If money was debited, contact support with your payment id.",
        )
        return redirect('payments:checkout', booking_id=booking.id)

    with transaction.atomic():
        payment.payment_method = 'ONLINE_RAZORPAY'
        payment.status = 'SUCCESS'
        payment.is_demo = False
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_order_id = razorpay_order_id
        payment.razorpay_signature = razorpay_signature
        payment.paid_at = timezone.now()
        payment.failure_reason = None
        payment.save()

        BookingStatusHistory.objects.create(
            booking=booking,
            from_status=booking.status,
            to_status=booking.status,
            changed_by=request.user,
            notes=f"Online payment of ₹{payment.amount} verified via Razorpay (Ref: {razorpay_payment_id}).",
        )
        Invoice.objects.get_or_create(
            booking=booking,
            defaults={
                'invoice_number': f"INV-{booking.booking_number.replace('HB-', '')}",
                'subtotal': booking.service_price,
                'total_amount': booking.total_amount,
            },
        )
        if booking.provider:
            notify(
                booking.provider.user,
                "Payment received",
                f"Booking {booking.booking_number} has been paid online (₹{payment.amount}).",
                'PAYMENT',
                f"/bookings/{booking.id}/",
            )

    messages.success(request, f" Payment of ₹{payment.amount} successful! Your booking is confirmed.")
    return redirect('bookings:detail', booking_id=booking.id)


@login_required
@require_POST
def cash_confirm(request, booking_id):
    """Customer opts for Cash on Service (no money captured at this point)."""
    booking = get_object_or_404(Booking, id=booking_id)
    if not _can_access_payment(request.user, booking):
        messages.error(request, "You are not authorised to change payment for this booking.")
        return redirect('core:home')

    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={'amount': booking.total_amount},
    )
    payment.payment_method = 'CASH'
    payment.status = 'PENDING'
    payment.cash_received_by_provider = False
    payment.save(update_fields=[
        'payment_method', 'status', 'cash_received_by_provider', 'updated_at',
    ])

    BookingStatusHistory.objects.create(
        booking=booking,
        from_status=booking.status,
        to_status=booking.status,
        changed_by=request.user,
        notes=(
            f"Customer selected Cash on Service — ₹{booking.total_amount} to be collected "
            "by the technician on completion."
        ),
    )

    messages.info(
        request,
        f"Cash on Service selected. Pay ₹{booking.total_amount} directly to the technician "
        "after the work proof is confirmed.",
    )
    return redirect('bookings:detail', booking_id=booking.id)


@login_required
def invoice_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    invoice = get_object_or_404(Invoice, booking=booking)

    if not _can_access_payment(request.user, booking):
        messages.error(request, "You are not authorised to view this invoice.")
        return redirect('core:home')

    return render(request, 'payments/invoice.html', {
        'booking': booking,
        'invoice': invoice,
        'title': f'Invoice {invoice.invoice_number}',
    })


@login_required
def payment_status(request, booking_id):
    """Small JSON endpoint so the tracking page can refresh payment state."""
    booking = get_object_or_404(Booking, id=booking_id)
    if not _can_access_payment(request.user, booking):
        return JsonResponse({'error': 'Not authorised'}, status=403)

    payment = getattr(booking, 'payment', None)
    if payment is None:
        return JsonResponse({'status': 'NONE'})

    return JsonResponse({
        'status': payment.status,
        'method': payment.payment_method,
        'amount': str(payment.amount),
        'is_demo': payment.is_demo,
        'settled': payment.is_settled,
        'razorpay_payment_id': payment.razorpay_payment_id or '',
    })


@login_required
def razorpay_webhook(request):
    """
    Server-to-server webhook from Razorpay.

    Signature is verified against RAZORPAY_WEBHOOK_SECRET before anything is
    trusted. This is the safety net for a browser that closes mid-payment.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    signature = request.headers.get('X-Razorpay-Signature', '')
    try:
        razorpay_service.verify_webhook_signature(request.body, signature)
    except razorpay_service.PaymentVerificationError as exc:
        logger.warning("Rejected Razorpay webhook: %s", exc)
        return JsonResponse({'error': 'invalid signature'}, status=400)

    try:
        event = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'error': 'invalid payload'}, status=400)

    event_type = event.get('event', '')
    payload = (event.get('payload') or {}).get('payment', {}).get('entity', {}) or {}
    order_id = payload.get('order_id')
    payment_id = payload.get('id')

    if not order_id:
        return JsonResponse({'status': 'ignored'})

    payment = Payment.objects.filter(razorpay_order_id=order_id).select_related('booking').first()
    if payment is None:
        return JsonResponse({'status': 'unknown_order'})

    if event_type == 'payment.captured' and payment.status != 'SUCCESS':
        with transaction.atomic():
            payment.status = 'SUCCESS'
            payment.razorpay_payment_id = payment_id
            payment.paid_at = timezone.now()
            payment.save(update_fields=['status', 'razorpay_payment_id', 'paid_at', 'updated_at'])
        logger.info("Webhook captured payment for booking %s", payment.booking.booking_number)

    elif event_type == 'payment.failed' and payment.status == 'PENDING':
        payment.status = 'FAILED'
        payment.failure_reason = (payload.get('error_description') or '')[:255]
        payment.save(update_fields=['status', 'failure_reason', 'updated_at'])

    elif event_type.startswith('refund.') and payment.status == 'SUCCESS':
        payment.status = 'REFUNDED'
        payment.razorpay_refund_id = payload.get('id')
        payment.save(update_fields=['status', 'razorpay_refund_id', 'updated_at'])

    return JsonResponse({'status': 'ok'})
