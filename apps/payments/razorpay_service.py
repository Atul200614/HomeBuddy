"""
Razorpay integration layer.

Two modes, both explicit and honest:

* LIVE  — ``RAZORPAY_KEY_ID`` + ``RAZORPAY_KEY_SECRET`` are set in ``.env``.
          Orders are created through the real Razorpay Orders API and every
          callback signature is verified with
          ``client.utility.verify_payment_signature`` using HMAC-SHA256.
* DEMO  — no keys configured. Orders get a deterministic local id and the
          checkout page itself is labelled "DEMO MODE". A demo payment is
          stored with ``is_demo=True`` so nobody can mistake it for real money.

Nothing in this module fakes a successful signature: in demo mode no signature
is ever claimed, and in live mode an invalid signature always raises.
"""
import hashlib
import hmac
import logging
import uuid

from django.conf import settings

logger = logging.getLogger('homebuddy.payments')

try:  # The SDK is optional at import time so the project boots without it.
    import razorpay
except ImportError:  # pragma: no cover
    razorpay = None


class RazorpayError(Exception):
    """Raised when the gateway rejects a request or a signature is invalid."""


class PaymentVerificationError(RazorpayError):
    """Raised when the callback signature does not match."""


def is_demo_mode():
    """True when we are not talking to the real gateway."""
    if getattr(settings, 'RAZORPAY_DEMO_MODE', True):
        return True
    return not (settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)


def get_client():
    """Return a configured Razorpay client, or None in demo mode."""
    if is_demo_mode():
        return None
    if razorpay is None:
        raise RazorpayError(
            "The 'razorpay' package is not installed. Run: pip install razorpay"
        )
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def _to_paise(amount):
    """Razorpay works in paise (1 INR = 100 paise)."""
    return int(round(float(amount) * 100))


def create_order(payment, receipt=None):
    """
    Create (or reuse) a Razorpay order for a Payment row.

    Returns a dict: {order_id, amount, currency, key_id, demo}
    """
    if payment.razorpay_order_id:
        return {
            'order_id': payment.razorpay_order_id,
            'amount': _to_paise(payment.amount),
            'currency': settings.RAZORPAY_CURRENCY,
            'key_id': settings.RAZORPAY_KEY_ID,
            'demo': is_demo_mode(),
        }

    receipt = receipt or f"rcpt_{payment.booking.booking_number}"

    if is_demo_mode():
        order_id = f"order_demo_{uuid.uuid4().hex[:14]}"
        payment.razorpay_order_id = order_id
        payment.is_demo = True
        payment.save(update_fields=['razorpay_order_id', 'is_demo', 'updated_at'])
        logger.info("DEMO order %s created for booking %s", order_id, payment.booking.booking_number)
        return {
            'order_id': order_id,
            'amount': _to_paise(payment.amount),
            'currency': settings.RAZORPAY_CURRENCY,
            'key_id': '',
            'demo': True,
        }

    client = get_client()
    try:
        order = client.order.create({
            'amount': _to_paise(payment.amount),
            'currency': settings.RAZORPAY_CURRENCY,
            'receipt': receipt[:40],
            'notes': {
                'booking_number': payment.booking.booking_number,
                'payment_id': str(payment.pk),
            },
        })
    except Exception as exc:  # razorpay raises its own error types
        logger.exception("Razorpay order creation failed")
        raise RazorpayError(f"Could not create a payment order: {exc}") from exc

    payment.razorpay_order_id = order['id']
    payment.is_demo = False
    payment.save(update_fields=['razorpay_order_id', 'is_demo', 'updated_at'])
    return {
        'order_id': order['id'],
        'amount': order['amount'],
        'currency': order.get('currency', settings.RAZORPAY_CURRENCY),
        'key_id': settings.RAZORPAY_KEY_ID,
        'demo': False,
    }


def verify_signature(order_id, payment_id, signature):
    """
    Verify the checkout callback signature.

    Uses the official SDK in live mode. In demo mode we never accept a
    signature at all — the caller must use the explicit demo path instead.
    """
    if is_demo_mode():
        raise PaymentVerificationError(
            "Signature verification is unavailable in demo mode."
        )

    if not all([order_id, payment_id, signature]):
        raise PaymentVerificationError("Incomplete payment payload.")

    client = get_client()
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })
    except Exception as exc:
        logger.warning("Signature verification failed for order %s", order_id)
        raise PaymentVerificationError("Payment signature could not be verified.") from exc
    return True


def verify_webhook_signature(body, signature):
    """
    Verify a Razorpay webhook using RAZORPAY_WEBHOOK_SECRET.

    Implemented directly with HMAC-SHA256 so it works even when the SDK is
    absent; this is exactly what the SDK does internally.
    """
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    if not secret:
        raise PaymentVerificationError("Webhook secret is not configured.")
    if not signature:
        raise PaymentVerificationError("Missing webhook signature.")

    if isinstance(body, str):
        body = body.encode('utf-8')

    expected = hmac.new(
        secret.encode('utf-8'), body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise PaymentVerificationError("Webhook signature mismatch.")
    return True


def fetch_payment(payment_id):
    """Fetch a payment from Razorpay (used by reconciliation)."""
    if is_demo_mode():
        return None
    client = get_client()
    try:
        return client.payment.fetch(payment_id)
    except Exception as exc:
        logger.exception("Could not fetch payment %s", payment_id)
        raise RazorpayError(str(exc)) from exc


def create_refund(payment_id, amount=None, notes=None):
    """Issue a (full or partial) refund for a captured Razorpay payment."""
    if is_demo_mode():
        return {'id': f'rfnd_demo_{uuid.uuid4().hex[:12]}', 'status': 'processed', 'demo': True}
    client = get_client()
    payload = {}
    if amount is not None:
        payload['amount'] = _to_paise(amount)
    if notes:
        payload['notes'] = notes
    try:
        return client.payment.refund(payment_id, payload)
    except Exception as exc:
        logger.exception("Refund failed for payment %s", payment_id)
        raise RazorpayError(f"Refund failed: {exc}") from exc
