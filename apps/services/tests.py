"""Services discovery, admin panel and notification tests."""
import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.models import Booking
from apps.customers.models import Address, CustomerProfile
from apps.notifications.models import Notification
from apps.professionals.models import ProviderProfile, VerificationDocument
from apps.services.models import Category, ProviderService, Service


class ServiceDiscoveryTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Plumbing', slug='plumbing')
        self.cheap = Service.objects.create(
            category=self.category, name='Tap Fix', slug='tap-fix',
            base_price=Decimal('199.00'), short_description='Fix a tap',
            detailed_description='Fix leaking tap',
        )
        self.expensive = Service.objects.create(
            category=self.category, name='Bathroom Fitting', slug='bathroom-fitting',
            base_price=Decimal('2499.00'), short_description='Full fitting',
            detailed_description='Install fittings',
        )

    def test_list_page_renders(self):
        response = self.client.get('/services/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tap Fix')

    def test_search_filters_results(self):
        response = self.client.get('/services/', {'q': 'Bathroom'})
        self.assertContains(response, 'Bathroom Fitting')
        self.assertNotContains(response, 'Tap Fix')

    def test_max_price_filter_applies(self):
        response = self.client.get('/services/', {'max_price': '500'})
        self.assertContains(response, 'Tap Fix')
        self.assertNotContains(response, 'Bathroom Fitting')

    def test_category_detail(self):
        response = self.client.get('/services/category/plumbing/')
        self.assertEqual(response.status_code, 200)

    def test_service_detail(self):
        response = self.client.get('/services/view/tap-fix/')
        self.assertEqual(response.status_code, 200)

    def test_invalid_max_price_does_not_crash(self):
        response = self.client.get('/services/', {'max_price': 'abc'})
        self.assertEqual(response.status_code, 200)


class AdminPanelTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='boss@example.com', email='boss@example.com',
            password='Str0ngPass!23', role='ADMIN', phone='9600000001',
        )
        self.admin.is_staff = True
        self.admin.save()
        self.client.force_login(self.admin)

    def test_all_admin_pages_render(self):
        for url in ['/admin-panel/', '/admin-panel/users/', '/admin-panel/verifications/',
                    '/admin-panel/bookings/', '/admin-panel/payments/',
                    '/admin-panel/payouts/', '/admin-panel/complaints/',
                    '/django-admin/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)

    def test_cannot_suspend_self(self):
        response = self.client.post(f'/admin-panel/users/{self.admin.id}/toggle-active/')
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)
        self.assertEqual(response.status_code, 302)

    def test_suspend_other_user(self):
        target = User.objects.create_user(
            username='victim@example.com', email='victim@example.com',
            password='Str0ngPass!23', role='CUSTOMER',
        )
        self.client.post(f'/admin-panel/users/{target.id}/toggle-active/')
        target.refresh_from_db()
        self.assertFalse(target.is_active)

    def test_toggle_requires_post(self):
        target = User.objects.create_user(
            username='v2@example.com', email='v2@example.com',
            password='Str0ngPass!23', role='CUSTOMER',
        )
        response = self.client.get(f'/admin-panel/users/{target.id}/toggle-active/')
        self.assertEqual(response.status_code, 405)


class KycTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='kyc@example.com', email='kyc@example.com',
            password='Str0ngPass!23', role='ADMIN', phone='9600000002',
        )
        self.provider_user = User.objects.create_user(
            username='kycp@example.com', email='kycp@example.com',
            password='Str0ngPass!23', role='PROVIDER', phone='9600000003',
        )
        self.provider = ProviderProfile.objects.create(
            user=self.provider_user, business_name='KYC Co', is_verified=False,
        )
        self.client.force_login(self.admin)

    def _doc(self, doc_type):
        return VerificationDocument.objects.create(
            provider=self.provider, document_type=doc_type,
            document_file='kyc_documents/test.pdf',
        )

    def test_identity_document_grants_verified_badge(self):
        doc = self._doc('AADHAAR')
        self.client.post(f'/admin-panel/verifications/{doc.id}/approve/')
        self.provider.refresh_from_db()
        self.assertTrue(self.provider.is_verified)
        doc.refresh_from_db()
        self.assertEqual(doc.status, 'APPROVED')

    def test_skill_certificate_alone_does_not_verify(self):
        doc = self._doc('SKILL_CERTIFICATE')
        self.client.post(f'/admin-panel/verifications/{doc.id}/approve/')
        self.provider.refresh_from_db()
        self.assertFalse(self.provider.is_verified)

    def test_rejection_records_note(self):
        doc = self._doc('PAN')
        self.client.post(
            f'/admin-panel/verifications/{doc.id}/reject/',
            {'admin_notes': 'Blurry scan'},
        )
        doc.refresh_from_db()
        self.assertEqual(doc.status, 'REJECTED')
        self.assertEqual(doc.admin_notes, 'Blurry scan')

    def test_approval_requires_post(self):
        doc = self._doc('AADHAAR')
        response = self.client.get(f'/admin-panel/verifications/{doc.id}/approve/')
        self.assertEqual(response.status_code, 405)


class NotificationTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='notifc@example.com', email='notifc@example.com',
            password='Str0ngPass!23', role='CUSTOMER', phone='9500000001',
        )
        self.customer_profile = CustomerProfile.objects.create(user=self.customer)
        self.address = Address.objects.create(
            user=self.customer, title='Home', address_line1='A1', pincode='411038',
        )
        self.provider_user = User.objects.create_user(
            username='notifp@example.com', email='notifp@example.com',
            password='Str0ngPass!23', role='PROVIDER', phone='9500000002',
        )
        self.provider = ProviderProfile.objects.create(
            user=self.provider_user, business_name='Notif Co',
            is_verified=True, is_available_today=True, service_pincodes='411038',
        )
        category = Category.objects.create(name='Pest', slug='pest')
        self.service = Service.objects.create(
            category=category, name='Pest Control', slug='pest-control',
            base_price=Decimal('999.00'), short_description='Pest',
            detailed_description='Pest control',
        )
        self.booking = Booking.objects.create(
            customer=self.customer_profile, provider=self.provider,
            service=self.service, address=self.address,
            scheduled_date=timezone.localdate() + datetime.timedelta(days=1),
            time_slot='10:00 AM - 12:00 PM',
            service_price=Decimal('999.00'), total_amount=Decimal('999.00'),
        )

    def test_accept_creates_notification_for_customer(self):
        self.client.force_login(self.provider_user)
        self.client.post(f'/provider/jobs/{self.booking.id}/accept/')
        self.assertTrue(
            Notification.objects.filter(
                user=self.customer, notification_type='BOOKING'
            ).exists()
        )

    def test_mark_read_requires_post(self):
        notif = Notification.objects.create(
            user=self.customer, title='Hi', message='Hello',
        )
        response = self.client.get(f'/notifications/{notif.id}/read/') if self.client.login(
            username='notifc@example.com', password='Str0ngPass!23'
        ) else None
        self.assertEqual(response.status_code, 405)
        notif.refresh_from_db()
        self.assertFalse(notif.is_read)

    def test_mark_read_post_works(self):
        notif = Notification.objects.create(
            user=self.customer, title='Hi', message='Hello',
        )
        self.client.force_login(self.customer)
        self.client.post(f'/notifications/{notif.id}/read/')
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
