"""Role based access control decorators."""
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def _guard(request, predicate, role_label, login_message):
    if not request.user.is_authenticated:
        messages.warning(request, login_message)
        return redirect('accounts:login')
    if not predicate:
        messages.error(request, f"Access restricted to {role_label} accounts.")
        return redirect('core:home')
    return None


def customer_required(view_func):
    """Allow only customers (and superusers, who are platform owners)."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        blocked = _guard(
            request,
            request.user.is_authenticated
            and (request.user.is_customer or request.user.is_superuser),
            "Customer",
            "Please log in to continue.",
        )
        return blocked or view_func(request, *args, **kwargs)

    return _wrapped


def provider_required(view_func):
    """Allow only service providers (and superusers)."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        blocked = _guard(
            request,
            request.user.is_authenticated
            and (request.user.is_provider or request.user.is_superuser),
            "Service Provider",
            "Please log in to your provider account.",
        )
        return blocked or view_func(request, *args, **kwargs)

    return _wrapped


def admin_required(view_func):
    """Allow only administrators / staff."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        blocked = _guard(
            request,
            request.user.is_authenticated
            and (
                request.user.is_admin_user
                or request.user.is_superuser
                or request.user.is_staff
            ),
            "Administrator",
            "Please log in as an administrator.",
        )
        return blocked or view_func(request, *args, **kwargs)

    return _wrapped
