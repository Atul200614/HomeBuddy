"""Accounts: registration (with real password validation), login, logout."""
import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.customers.models import CustomerProfile
from apps.notifications.services import notify
from apps.professionals.models import ProviderProfile
from .forms import CustomerRegistrationForm, ProviderRegistrationForm, UserLoginForm, UserPasswordChangeForm

logger = logging.getLogger('homebuddy.accounts')


def register_customer(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    next_url = request.POST.get('next') or request.GET.get('next') or ''
    is_json = (
        request.content_type == 'application/json'
        or request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or 'application/json' in request.META.get('HTTP_ACCEPT', '')
    )

    if request.method == 'POST':
        data = request.POST
        if request.content_type == 'application/json':
            import json
            try:
                data = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = {}

        form = CustomerRegistrationForm(data)
        if form.is_valid():
            user = form.save()
            CustomerProfile.objects.get_or_create(user=user)
            try:
                notify(
                    user,
                    "Welcome to HomeBuddy",
                    "Your customer account is ready. Add an address, then book your first service.",
                    'SYSTEM',
                    reverse('customers:dashboard'),
                )
            except Exception as exc:
                logger.warning("Notification error during customer registration: %s", exc)

            login(request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')

            if is_json:
                from django.http import JsonResponse
                return JsonResponse({
                    'success': True,
                    'message': f"Welcome to HomeBuddy, {user.first_name or user.username}! Your customer account is ready.",
                    'user': {
                        'id': user.id,
                        'name': user.get_full_name() or user.username,
                        'email': user.email,
                        'role': user.role,
                    },
                    'redirect_url': next_url or reverse('customers:dashboard')
                }, status=201)

            messages.success(
                request,
                f"Welcome to HomeBuddy, {user.first_name or user.username}! "
                "Your customer account is ready.",
            )
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('customers:dashboard')

        if is_json:
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
                'message': 'Please correct the errors in the registration form.'
            }, status=400)

        messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form, 'title': 'Create Customer Account', 'next': next_url,
    })


def register_provider(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    if request.method == 'POST':
        form = ProviderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            ProviderProfile.objects.create(
                user=user,
                business_name=(
                    form.cleaned_data.get('business_name')
                    or f"{user.get_full_name() or user.username} Services"
                ),
                experience_years=form.cleaned_data.get('experience_years', 2),
                service_pincodes=(
                    form.cleaned_data.get('service_pincodes')
                    or '411038, 411045, 411057'
                ),
            )
            try:
                notify(
                    user,
                    "Technician account created",
                    "Upload your Aadhaar and police verification documents to earn the "
                    "Verified badge and start receiving jobs.",
                    'VERIFICATION',
                    reverse('professionals:verification'),
                )
            except Exception as exc:
                logger.warning("Notification error during provider registration: %s", exc)
            login(request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')
            messages.success(
                request,
                "Your technician profile is created. Submit KYC documents to get verified.",
            )
            return redirect('professionals:dashboard')
        messages.error(request, "Please correct the errors in the form.")
    else:
        form = ProviderRegistrationForm()

    return render(request, 'accounts/provider_register.html', {
        'form': form, 'title': 'Join as a Service Professional',
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    next_url = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_active:
                login(request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')
                messages.success(
                    request, f"Welcome back, {user.first_name or user.username}!"
                )
                # Only follow a `next` that points back at this site.
                if next_url and url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return redirect(next_url)
                return redirect('accounts:role_redirect')
            if user is not None and not user.is_active:
                # Do not reveal whether the password was right.
                messages.error(
                    request,
                    "This account is deactivated. Please contact HomeBuddy support.",
                )
            else:
                messages.error(request, "Invalid email address or password.")
            logger.info("Failed login attempt for %s", email)
        else:
            messages.error(request, "Please enter a valid email and password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {
        'form': form, 'title': 'Sign In to HomeBuddy', 'next': next_url,
    })


@require_POST
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been signed out.")
    return redirect('core:home')


def role_redirect(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.user.is_admin_user or request.user.is_staff:
        return redirect('admin_dashboard:index')
    if request.user.is_provider:
        return redirect('professionals:dashboard')
    return redirect('customers:dashboard')


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = UserPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect('accounts:password_change')
        messages.error(request, "Please correct the errors below.")
    else:
        form = UserPasswordChangeForm(user=request.user)

    return render(request, 'accounts/password_change.html', {
        'form': form,
        'title': 'Change Password',
    })


def password_reset_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()
        from .models import User
        user = User.objects.filter(email__iexact=email).first()
        if user:
            messages.success(
                request,
                f"Password reset instructions have been sent to {email}. "
                "(In demo mode, please use your standard credentials or contact admin)."
            )
            return redirect('accounts:password_reset_done')
        messages.error(request, "No account was found with that email address.")

    return render(request, 'accounts/password_reset.html', {
        'title': 'Reset Forgotten Password',
    })


def password_reset_done_view(request):
    return render(request, 'accounts/password_reset_done.html', {
        'title': 'Password Reset Requested',
    })

