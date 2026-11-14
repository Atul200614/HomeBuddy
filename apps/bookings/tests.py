"""Booking engine tests: creation, validation, state machine, work proof."""
import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.models import Booking, BookingStatusHistory, WorkProof
from apps.customers.models import Address, CustomerProfile
from apps.payments.models import EarningsLedger, Invoice
from apps.professionals.models import ProviderProfile
from apps.services.models import Category, Service


def make_user(email, role, phone):
    return User.objects.create_user(
        username=email, email=email, password='Str0ngPass!23',
        role=role, phone=phone, first_name=role.title(),
    )


class BookingTestBase(TestCase):
    def setUp(self):
        self.customer = make_user('cust@example.com', 'CUSTOMER', '9800000001')
        self.customer_profile = CustomerProfile.objects.create(user=self.customer)
        self.address = Address.objects.create(
            user=self.customer, title='Home', address_line1='Flat 1',
            address_line2='Kothrud', city='Pune', pincode='411038', is_default=True,
        )
        self.provider_user = make_user('prov@example.com', 'PROVIDER', '9800000002')
        self.provider = ProviderProfile.objects.create(
            user=self.provider_user, business_name='Clean Co',
            is_verified=True, is_available_today=True,
            service_pincodes='411038, 411045',
        )
        self.category = Category.objects.create(name='Cleaning', slug='cleaning')
        self.service = Service.objects.create(
            category=self.category, name='2 BHK Deep Cleaning',
            slug='2-bhk-deep-cleaning', base_price=Decimal('2999.00'),
            is_emergency_eligible=True, emergency_surcharge=Decimal('199.00'),
            short_description='Deep clean', detailed_description='Deep clean 2BHK',
        )
        self.cheap_service = Service.objects.create(
            category=self.category, name='Fan Repair',
            slug='fan-repair', base_price=Decimal('299.00'),
            is_emergency_eligible=False,
            short_description='Fan repair', detailed_description='Fan repair',
        )
        self.client.force_login(self.customer)

    def post_booking(self, service_slug='2-bhk-deep-cleaning', **overrides):
        payload = {
            'address': self.address.id,
            'provider': self.provider.id,
            'scheduled_date': (timezone.localdate() + datetime.timedelta(days=2)).isoformat(),
            'time_slot': '10:00 AM - 12:00 PM',
            'special_instructions': 'Ring the bell twice',
        }
        payload.update(overrides)
        return self.client.post(f'/bookings/create/{service_slug}/', payload)


class BookingCreationTests(BookingTestBase):
    def test_booking_created_with_correct_total(self):
        response = self.post_booking()
        self.assertEqual(response.status_code, 302)
        booking = Booking.objects.get(customer=self.customer_profile)
        self.assertEqual(booking.status, 'REQUESTED')
        self.assertEqual(booking.total_amount, Decimal('2999.00'))
        self.assertEqual(booking.service_price, Decimal('2999.00'))
        self.assertEqual(booking.emergency_fee, Decimal('0.00'))
        self.assertTrue(
            BookingStatusHistory.objects.filter(booking=booking, to_status='REQUESTED').exists()
        )

    def test_emergency_surcharge_applied(self):
        self.post_booking(is_emergency='on')
        booking = Booking.objects.get(customer=self.customer_profile)
        self.assertTrue(booking.is_emergency)
        self.assertEqual(booking.emergency_fee, Decimal('199.00'))
        self.assertEqual(booking.total_amount, Decimal('3198.00'))
        self.assertEqual(booking.scheduled_date, timezone.localdate())

    def test_emergency_rejected_for_ineligible_service(self):
        response = self.post_booking(service_slug='fan-repair', is_emergency='on')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Booking.objects.filter(service=self.cheap_service).exists())

    def test_past_date_rejected(self):
        response = self.post_booking(
            scheduled_date=(timezone.localdate() - datetime.timedelta(days=1)).isoformat()
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Booking.objects.exists())

    def test_date_beyond_90_days_rejected(self):
        response = self.post_booking(
            scheduled_date=(timezone.localdate() + datetime.timedelta(days=120)).isoformat()
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Booking.objects.exists())

    def test_slot_conflict_prevents_double_booking(self):
        self.post_booking()
        self.assertEqual(Booking.objects.count(), 1)
        # Same provider, same date, same slot -> must not create a second booking
        response = self.post_booking()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), 1)

    def test_auto_assignment_uses_pincode(self):
        response = self.post_booking(provider='')
        self.assertEqual(response.status_code, 302)
        booking = Booking.objects.get(customer=self.customer_profile)
        self.assertEqual(booking.provider_id, self.provider.id)

    def test_booking_with_inline_new_address(self):
        """A customer with no saved address enters delivery address directly on Step 2."""
        new_customer = make_user('newcust@example.com', 'CUSTOMER', '9700000001')
        CustomerProfile.objects.create(user=new_customer)
        self.client.force_login(new_customer)

        payload = {
            'address': '',
            'customer_name': 'New Customer',
            'customer_phone': '9700000001',
            'address_title': 'Home',
            'house_flat_no': 'B-304, Green Heights',
            'street': 'Near Balewadi High Street',
            'area': 'Balewadi',
            'city': 'Pune',
            'state': 'Maharashtra',
            'pincode': '411045',
            'scheduled_date': (timezone.localdate() + datetime.timedelta(days=3)).isoformat(),
            'time_slot': '02:00 PM - 04:00 PM',
            'special_instructions': 'Call when arrived',
        }
        response = self.client.post('/bookings/create/2-bhk-deep-cleaning/', payload)
        self.assertEqual(response.status_code, 302)

        booking = Booking.objects.get(customer__user=new_customer)
        # MUST redirect directly to payment checkout, NEVER to login
        self.assertEqual(response['Location'], f'/payments/checkout/{booking.id}/')
        self.assertNotIn('/accounts/login/', response['Location'])
        self.assertIsNotNone(booking.address)
        self.assertEqual(booking.address.pincode, '411045')
        self.assertEqual(booking.address.city, 'Pune')
        self.assertEqual(booking.status, 'REQUESTED')
        self.assertTrue(Address.objects.filter(user=new_customer, pincode='411045').exists())

    def test_inline_address_validation_missing_pincode(self):
        """Submitting an invalid PIN code on Step 2 re-renders the form with field error."""
        new_customer = make_user('invalidpin@example.com', 'CUSTOMER', '9700000002')
        CustomerProfile.objects.create(user=new_customer)
        self.client.force_login(new_customer)

        payload = {
            'address': '',
            'customer_name': 'Invalid Pin Customer',
            'customer_phone': '9700000002',
            'house_flat_no': 'Flat 101',
            'area': 'Kothrud',
            'city': 'Pune',
            'pincode': '123',  # Invalid PIN (must be 6 digits)
            'scheduled_date': (timezone.localdate() + datetime.timedelta(days=1)).isoformat(),
            'time_slot': '10:00 AM - 12:00 PM',
        }
        response = self.client.post('/bookings/create/2-bhk-deep-cleaning/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Booking.objects.filter(customer__user=new_customer).exists())


class BookingStateMachineTests(BookingTestBase):
    def setUp(self):
        super().setUp()
        self.booking = Booking.objects.create(
            customer=self.customer_profile, provider=self.provider,
            service=self.service, address=self.address,
            scheduled_date=timezone.localdate() + datetime.timedelta(days=1),
            time_slot='10:00 AM - 12:00 PM',
            service_price=Decimal('2999.00'), total_amount=Decimal('2999.00'),
            status='REQUESTED',
        )

    def transition(self, new_status):
        return self.client.post(
            f'/provider/jobs/{self.booking.id}/status/{new_status}/'
        )

    def test_valid_path_through_states(self):
        self.client.force_login(self.provider_user)
        self.client.post(f'/provider/jobs/{self.booking.id}/accept/')
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'ACCEPTED')

        for state in ('EN_ROUTE', 'ARRIVED', 'IN_PROGRESS'):
            self.transition(state)
            self.booking.refresh_from_db()
            self.assertEqual(self.booking.status, state)

    def test_illegal_transition_refused(self):
        self.client.force_login(self.provider_user)
        self.transition('COMPLETED')
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'REQUESTED')

    def test_cancel_via_get_does_not_mutate(self):
        response = self.client.get(f'/bookings/{self.booking.id}/cancel/')
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'REQUESTED')
        self.assertEqual(response.status_code, 302)

    def test_cancel_via_post_works(self):
        response = self.client.post(
            f'/bookings/{self.booking.id}/cancel/',
            {'cancellation_reason': 'Changed my mind'},
        )
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'CANCELLED')
        self.assertEqual(self.booking.cancellation_reason, 'Changed my mind')

    def test_other_customer_cannot_cancel(self):
        intruder = make_user('intruder@example.com', 'CUSTOMER', '9800000009')
        CustomerProfile.objects.create(user=intruder)
        self.client.force_login(intruder)
        self.client.post(f'/bookings/{self.booking.id}/cancel/', {'cancellation_reason': 'x'})
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'REQUESTED')


class WorkProofAndCompletionTests(BookingTestBase):
    def setUp(self):
        super().setUp()
        self.booking = Booking.objects.create(
            customer=self.customer_profile, provider=self.provider,
            service=self.service, address=self.address,
            scheduled_date=timezone.localdate() + datetime.timedelta(days=1),
            time_slot='10:00 AM - 12:00 PM',
            service_price=Decimal('2999.00'), total_amount=Decimal('2999.00'),
            status='WORK_PROOF_SUBMITTED',
        )

    def test_completion_requires_work_proof(self):
        response = self.client.post(
            f'/bookings/{self.booking.id}/confirm/', {'feedback': 'Great'}
        )
        self.assertEqual(response.status_code, 404)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'WORK_PROOF_SUBMITTED')

    def test_completion_creates_ledger_and_invoice(self):
        WorkProof.objects.create(
            booking=self.booking, work_notes='Cleaned everything',
            submitted_at=timezone.now(),
        )
        response = self.client.post(
            f'/bookings/{self.booking.id}/confirm/', {'feedback': 'Excellent work'}
        )
        self.assertEqual(response.status_code, 302)

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'COMPLETED')

        ledger = EarningsLedger.objects.get(booking=self.booking)
        self.assertEqual(ledger.gross_amount, Decimal('2999.00'))
        self.assertEqual(ledger.commission_amount, Decimal('299.90'))
        self.assertEqual(ledger.net_earnings, Decimal('2699.10'))

        invoice = Invoice.objects.get(booking=self.booking)
        self.assertEqual(invoice.total_amount, Decimal('2999.00'))

    def test_completion_is_idempotent_for_ledger(self):
        WorkProof.objects.create(
            booking=self.booking, work_notes='Done', submitted_at=timezone.now(),
        )
        self.client.post(f'/bookings/{self.booking.id}/confirm/', {'feedback': 'Good'})
        # A second attempt must not duplicate the ledger or invoice
        self.client.post(f'/bookings/{self.booking.id}/confirm/', {'feedback': 'Again'})
        self.assertEqual(EarningsLedger.objects.filter(booking=self.booking).count(), 1)
        self.assertEqual(Invoice.objects.filter(booking=self.booking).count(), 1)


class BookingAccessTests(BookingTestBase):
    def setUp(self):
        super().setUp()
        self.booking = Booking.objects.create(
            customer=self.customer_profile, provider=self.provider,
            service=self.service, address=self.address,
            scheduled_date=timezone.localdate() + datetime.timedelta(days=1),
            time_slot='10:00 AM - 12:00 PM',
            service_price=Decimal('2999.00'), total_amount=Decimal('2999.00'),
            status='REQUESTED',
        )

    def test_other_customer_cannot_view_booking(self):
        intruder = make_user('spy@example.com', 'CUSTOMER', '9800000010')
        CustomerProfile.objects.create(user=intruder)
        self.client.force_login(intruder)
        response = self.client.get(f'/bookings/{self.booking.id}/')
        self.assertEqual(response.status_code, 302)

    def test_owner_can_view_booking(self):
        response = self.client.get(f'/bookings/{self.booking.id}/')
        self.assertEqual(response.status_code, 200)

    def test_provider_can_view_assigned_booking(self):
        self.client.force_login(self.provider_user)
        response = self.client.get(f'/bookings/{self.booking.id}/')
        self.assertEqual(response.status_code, 200)


class LocationTrackingTests(BookingTestBase):
    def setUp(self):
        super().setUp()
        self.address.latitude = Decimal('18.507400')
        self.address.longitude = Decimal('73.807700')
        self.address.save()

        self.booking = Booking.objects.create(
            customer=self.customer_profile, provider=self.provider,
            service=self.service, address=self.address,
            scheduled_date=timezone.localdate(),
            time_slot='10:00 AM - 12:00 PM',
            service_price=Decimal('2999.00'), total_amount=Decimal('2999.00'),
            status='EN_ROUTE',
        )

    def test_provider_can_post_live_location(self):
        self.client.force_login(self.provider_user)
        response = self.client.post(
            f'/bookings/{self.booking.id}/location/update/',
            data='{"latitude": 18.512000, "longitude": 73.815000, "speed": 30.0}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'ok')
        self.assertEqual(self.booking.location_updates.count(), 1)

    def test_customer_can_retrieve_live_location_and_eta(self):
        from apps.bookings.models import LocationUpdate
        LocationUpdate.objects.create(
            booking=self.booking, provider=self.provider,
            latitude=Decimal('18.512000'), longitude=Decimal('73.815000'),
            speed=Decimal('30.0')
        )
        # Customer requests tracking
        self.client.force_login(self.customer)
        response = self.client.get(f'/bookings/{self.booking.id}/location/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('available'))
        self.assertIn('eta_text', data)
        self.assertIn('distance_km', data)

    def test_unauthorized_user_cannot_view_location(self):
        intruder = make_user('intruder@example.com', 'CUSTOMER', '9800000099')
        CustomerProfile.objects.create(user=intruder)
        self.client.force_login(intruder)
        response = self.client.get(f'/bookings/{self.booking.id}/location/')
        self.assertEqual(response.status_code, 403)

