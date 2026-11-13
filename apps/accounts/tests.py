"""Account & access-control tests."""
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.customers.models import CustomerProfile
from apps.professionals.models import ProviderProfile


class RegistrationTests(TestCase):
    def test_customer_registration_creates_profile(self):
        response = self.client.post(reverse('accounts:register_customer'), {
            'first_name': 'Test', 'last_name': 'User',
            'email': 'new.customer@example.com', 'phone': '9876500001',
            'password': 'Str0ngPass!23', 'confirm_password': 'Str0ngPass!23',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='new.customer@example.com')
        self.assertEqual(user.role, 'CUSTOMER')
        self.assertTrue(CustomerProfile.objects.filter(user=user).exists())
        # Password must be hashed, never stored raw
        self.assertNotEqual(user.password, 'Str0ngPass!23')
        self.assertTrue(user.check_password('Str0ngPass!23'))

    def test_numeric_password_is_rejected(self):
        response = self.client.post(reverse('accounts:register_customer'), {
            'first_name': 'Weak', 'last_name': 'Pass',
            'email': 'weak@example.com', 'phone': '9876500002',
            'password': '12345678', 'confirm_password': '12345678',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='weak@example.com').exists())

    def test_mismatched_passwords_rejected(self):
        response = self.client.post(reverse('accounts:register_customer'), {
            'first_name': 'Mis', 'last_name': 'Match',
            'email': 'mismatch@example.com', 'phone': '9876500003',
            'password': 'Str0ngPass!23', 'confirm_password': 'Different!23',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='mismatch@example.com').exists())

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            username='dup@example.com', email='dup@example.com', password='Str0ngPass!23'
        )
        response = self.client.post(reverse('accounts:register_customer'), {
            'first_name': 'Dup', 'last_name': 'User',
            'email': 'dup@example.com', 'phone': '9876500004',
            'password': 'Str0ngPass!23', 'confirm_password': 'Str0ngPass!23',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='dup@example.com').count(), 1)

    def test_short_phone_rejected(self):
        response = self.client.post(reverse('accounts:register_customer'), {
            'first_name': 'Bad', 'last_name': 'Phone',
            'email': 'badphone@example.com', 'phone': '12345',
            'password': 'Str0ngPass!23', 'confirm_password': 'Str0ngPass!23',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='badphone@example.com').exists())

    def test_provider_registration_creates_profile(self):
        response = self.client.post(reverse('accounts:register_provider'), {
            'first_name': 'Pro', 'last_name': 'Tech',
            'email': 'new.provider@example.com', 'phone': '9876500005',
            'password': 'Str0ngPass!23', 'confirm_password': 'Str0ngPass!23',
            'business_name': 'Pro Tech Services',
            'experience_years': 5,
            'service_pincodes': '411001, 411002',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='new.provider@example.com')
        self.assertEqual(user.role, 'PROVIDER')
        self.assertTrue(ProviderProfile.objects.filter(user=user).exists())

    def test_invalid_pincode_rejected(self):
        response = self.client.post(reverse('accounts:register_provider'), {
            'first_name': 'Bad', 'last_name': 'Pin',
            'email': 'badpin@example.com', 'phone': '9876500006',
            'password': 'Str0ngPass!23', 'confirm_password': 'Str0ngPass!23',
            'experience_years': 2, 'service_pincodes': '411001, 99',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='badpin@example.com').exists())


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cust@example.com', email='cust@example.com',
            password='Str0ngPass!23', role='CUSTOMER',
            first_name='Cust', phone='9876511111',
        )
        CustomerProfile.objects.create(user=self.user)

    def test_login_succeeds_with_email(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'cust@example.com', 'password': 'Str0ngPass!23',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_wrong_password_fails(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'cust@example.com', 'password': 'nope',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_open_redirect_is_ignored(self):
        response = self.client.post(
            reverse('accounts:login') + '?next=https://evil.example.com',
            {'email': 'cust@example.com', 'password': 'Str0ngPass!23', 'next': 'https://evil.example.com'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('evil.example.com', response['Location'])

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)

    def test_logout_post_clears_session(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)


class RoleIsolationTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='c@example.com', email='c@example.com',
            password='Str0ngPass!23', role='CUSTOMER',
        )
        CustomerProfile.objects.create(user=self.customer)
        self.provider_user = User.objects.create_user(
            username='p@example.com', email='p@example.com',
            password='Str0ngPass!23', role='PROVIDER',
        )
        ProviderProfile.objects.create(
            user=self.provider_user, business_name='P Services'
        )

    def test_guest_redirected_from_portals(self):
        for url in ['/customer/dashboard/', '/provider/dashboard/', '/admin-panel/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, url)
            self.assertIn('/accounts/login/', response['Location'])

    def test_customer_cannot_open_provider_portal(self):
        self.client.force_login(self.customer)
        response = self.client.get('/provider/dashboard/')
        self.assertEqual(response.status_code, 302)

    def test_provider_cannot_open_customer_portal(self):
        self.client.force_login(self.provider_user)
        response = self.client.get('/customer/dashboard/')
        self.assertEqual(response.status_code, 302)

    def test_non_staff_cannot_open_admin_panel(self):
        self.client.force_login(self.customer)
        response = self.client.get('/admin-panel/')
        self.assertEqual(response.status_code, 302)
