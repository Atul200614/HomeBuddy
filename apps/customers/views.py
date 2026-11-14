"""Customer portal: dashboard, profile, addresses, booking history."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.accounts.decorators import customer_required
from apps.bookings.models import Booking
from .forms import AddressForm, CustomerProfileForm, CustomerUserEditForm
from .models import Address, CustomerProfile

PAGE_SIZE = 10


@login_required
@customer_required
def dashboard(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    bookings = Booking.objects.filter(customer=profile)
    recent_bookings = bookings.select_related('service', 'provider').order_by('-created_at')[:5]
    counts = bookings.aggregate(
        active=Count('id', filter=Q(status__in=[
            'REQUESTED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED',
            'IN_PROGRESS', 'WORK_PROOF_SUBMITTED',
        ])),
        completed=Count('id', filter=Q(status='COMPLETED')),
        cancelled=Count('id', filter=Q(status='CANCELLED')),
        spend=Sum('total_amount', filter=Q(status='COMPLETED')),
    )

    return render(request, 'customer/dashboard.html', {
        'profile': profile,
        'recent_bookings': recent_bookings,
        'active_bookings_count': counts['active'] or 0,
        'completed_bookings_count': counts['completed'] or 0,
        'cancelled_bookings_count': counts['cancelled'] or 0,
        'total_spend': counts['spend'] or 0,
        'saved_addresses': Address.objects.filter(user=request.user),
        'title': 'Customer Dashboard',
    })


@login_required
@customer_required
def profile_view(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = CustomerUserEditForm(request.POST, request.FILES, instance=request.user)
        p_form = CustomerProfileForm(request.POST, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile details have been updated.")
            return redirect('customers:profile')
        messages.error(request, "Please correct the highlighted fields.")
    else:
        u_form = CustomerUserEditForm(instance=request.user)
        p_form = CustomerProfileForm(instance=profile)

    return render(request, 'customer/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
        'title': 'Manage Profile',
    })


@login_required
@customer_required
def addresses_view(request):
    addresses = Address.objects.filter(user=request.user)
    next_url = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            addr.save()
            messages.success(request, f"Address '{addr.get_title_display()}' saved.")
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('customers:addresses')
        messages.error(request, "Please correct the address details.")
    else:
        form = AddressForm()

    return render(request, 'customer/addresses.html', {
        'addresses': addresses,
        'form': form,
        'title': 'Saved Addresses',
        'next': next_url,
    })


@login_required
@customer_required
@require_POST
def delete_address(request, address_id):
    """POST-only: deleting via a GET link was a CSRF hole."""
    addr = get_object_or_404(Address, id=address_id, user=request.user)

    if Booking.objects.filter(address=addr, status__in=[
        'REQUESTED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED', 'IN_PROGRESS',
        'WORK_PROOF_SUBMITTED',
    ]).exists():
        messages.error(
            request,
            "This address is used by an active booking and cannot be removed yet.",
        )
        return redirect('customers:addresses')

    addr.delete()
    messages.info(request, "Address removed.")
    return redirect('customers:addresses')


@login_required
@customer_required
def booking_history(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    status_filter = (request.GET.get('status') or '').strip()

    bookings = (
        Booking.objects.filter(customer=profile)
        .select_related('service', 'provider', 'address')
        .order_by('-created_at')
    )
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    paginator = Paginator(bookings, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'customer/bookings.html', {
        'bookings': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'querystring': query_params.urlencode(),
        'selected_status': status_filter,
        'title': 'Booking History',
    })
