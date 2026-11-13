"""Payment tests: demo flow, signature refusal, cash, ownership."""
import datetime
from decimal import Decimal

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.models import Booking
from apps.customers.models import Address, CustomerProfile
from apps.payments import razorpay_service
from apps.payments.models import Invoice, Payment
from apps.professionals.models import ProviderProfile
from apps.services.models import Category, Service


def make_user(email, role, phone):
    return User.objects.create_user(
        username=email, email=email, password='Str0ngPass!23',
        role=role, phone=phone, first_name=role.title(),
    )


class PaymentTestBase(TestCase):
    def setUp(self):
        self.customer = make_user('paycust@example.com', 'CUSTOMER', '9700000001')
        self.customer_profile = CustomerProfile.objects.create(user=self.customer)
        self.address = Address.objects.create(
            user=self.customer, title='Home', address_line1='Flat 9',
            city='Pune', pincode='411038',
        )
        self.provider_user = make_user('payprov@example.com', 'PROVIDER', '9700000002')
        self.provider = ProviderProfile.objects.create(
            user=self.provider_user, business_name='Pay Co', is_verified=True,
        )
        category = Category.objects.create(name='Repairs', slug='repairs')
        self.service = Service.objects.create(
            category=category, name='AC Service', slug='ac-service',
            base_price=Decimal('1500.00'), short_description='AC',
            detailed_description='AC service',
        )
        self.booking = Booking.objects.create(
            customer=self.customer_profile, provider=self.provider,
            service=self.service, address=self.address,
            scheduled_date=timezone.localdate() + datetime.timedelta(days=1),
            time_slot='10:00 AM - 12:00 PM',
            service_price=Decimal('1500.00'), total_amount=Decimal('1500.00'),
            status='REQUESTED',
        )
        self.client.force_login(self.customer)


class DemoModeTests(PaymentTestBase):
    def test_demo_mode_detected_with_empty_keys(self):
        self.assertTrue(razorpay_service.is_demo_mode())

    def test_checkout_renders_demo_banner(self):
        response = self.client.get(f'/payments/checkout/{self.booking.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'DEMO MODE')

    def test_order_created_in_demo_mode(self):
        response = self.client.get(f'/payments/checkout/{self.booking.id}/')
        payment = Payment.objects.get(booking=self.booking)
        self.assertTrue(payment.razorpay_order_id.startswith('order_demo_'))
        self.assertTrue(payment.is_demo)

    def test_demo_callback_requires_explicit_confirmation(self):
        payment = Payment.objects.create(
            booking=self.booking, amount=self.booking.total_amount
        )
        self.client.post(f'/payments/callback/{self.booking.id}/', {})
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'PENDING')

    def test_demo_callback_records_flagged_payment(self):
        payment = Payment.objects.create(
            booking=self.booking, amount=self.booking.total_amount
        )
        self.client.post(
            f'/payments/callback/{self.booking.id}/', {'demo_confirm': '1'}
        )
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'SUCCESS')
        self.assertTrue(payment.is_demo)
        self.assertEqual(payment.razorpay_signature, '')
        self.assertTrue(Invoice.objects.filter(booking=self.booking).exists())

    def test_signature_verification_refused_in_demo_mode(self):
        with self.assertRaises(razorpay_service.PaymentVerificationError):
            razorpay_service.verify_signature('order_x', 'pay_x', 'sig_x')

    def test_cash_choice_stays_pending(self):
        Payment.objects.create(booking=self.booking, amount=self.booking.total_amount)
        self.client.post(f'/payments/cash-confirm/{self.booking.id}/')
        payment = Payment.objects.get(booking=self.booking)
        self.assertEqual(payment.payment_method, 'CASH')
        self.assertEqual(payment.status, 'PENDING')
        self.assertFalse(payment.is_settled)

    def test_cash_not_settled_until_collected(self):
        payment = Payment.objects.create(
            booking=self.booking, amount=self.booking.total_amount,
            payment_method='CASH', status='SUCCESS',
            cash_received_by_provider=False,
        )
        self.assertFalse(payment.is_settled)
        payment.cash_received_by_provider = True
        self.assertTrue(payment.is_settled)


@override_settings(
    RAZORPAY_KEY_ID='rzp_test_dummy',
    RAZORPAY_KEY_SECRET='dummy_secret',
    RAZORPAY_DEMO_MODE=False,
)
class LiveModeTests(PaymentTestBase):
    def test_demo_mode_is_false_with_keys(self):
        self.assertFalse(razorpay_service.is_demo_mode())

    def test_invalid_signature_marks_payment_failed(self):
        payment = Payment.objects.create(
            booking=self.booking, amount=self.booking.total_amount,
            razorpay_order_id='order_real_1',
        )
        self.client.post(f'/payments/callback/{self.booking.id}/', {
            'razorpay_order_id': 'order_real_1',
            'razorpay_payment_id': 'pay_real_1',
            'razorpay_signature': 'totally_invalid_signature',
        })
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'FAILED')
        self.assertFalse(Invoice.objects.filter(booking=self.booking).exists())

    def test_missing_payload_does_not_confirm(self):
        payment = Payment.objects.create(
            booking=self.booking, amount=self.booking.total_amount
        )
        self.client.post(f'/payments/callback/{self.booking.id}/', {})
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'FAILED')

    def test_webhook_rejects_bad_signature(self):
        response = self.client.post(
            '/payments/webhook/razorpay/',
            data='{"event":"payment.captured"}',
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='bad',
        )
        self.assertEqual(response.status_code, 400)


class PaymentAccessTests(PaymentTestBase):
    def test_other_customer_cannot_checkout(self):
        intruder = make_user('thief@example.com', 'CUSTOMER', '9700000003')
        CustomerProfile.objects.create(user=intruder)
        self.client.force_login(intruder)
        response = self.client.get(f'/payments/checkout/{self.booking.id}/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Payment.objects.filter(booking=self.booking).exists())

    def test_cash_confirm_requires_post(self):
        Payment.objects.create(booking=self.booking, amount=self.booking.total_amount)
        response = self.client.get(f'/payments/cash-confirm/{self.booking.id}/')
        self.assertEqual(response.status_code, 405)

    def test_api_returns_only_own_payments(self):
        other = make_user('other@example.com', 'CUSTOMER', '9700000004')
        other_profile = CustomerProfile.objects.create(user=other)
        other_booking = Booking.objects.create(
            customer=other_profile, provider=self.provider,
            service=self.service, address=Address.objects.create(
                user=other, address_line1='Elsewhere', pincode='411001'
            ),
            scheduled_date=timezone.localdate() + datetime.timedelta(days=2),
            time_slot='10:00 AM - 12:00 PM',
            service_price=Decimal('1500.00'), total_amount=Decimal('1500.00'),
        )
        Payment.objects.create(booking=other_booking, amount=Decimal('1500.00'))
        Payment.objects.create(booking=self.booking, amount=Decimal('1500.00'))

        response = self.client.get('/api/v1/payments/my/')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['booking_number'], self.booking.booking_number)

    def test_anonymous_api_rejected(self):
        self.client.logout()
        response = self.client.get('/api/v1/payments/my/')
        self.assertIn(response.status_code, (401, 403))
