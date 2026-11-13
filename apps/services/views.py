"""Services catalogue: discovery, search, real filtering, pagination."""
import logging

from django.core.paginator import Paginator
from django.db.models import Count, Min, Q
from django.shortcuts import get_object_or_404, render

from apps.professionals.models import ProviderProfile
from .models import Category, ProviderService, Service

logger = logging.getLogger('homebuddy.services')

PAGE_SIZE = 9


def _int_or_none(raw):
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def services_list(request):
    """
    Catalogue with working filters.

    Filters are applied to the queryset (not merely echoed back):
      q          free text across name/description/category
      category   category slug
      pincode    only services with a verified provider covering that pincode
      verified   only services with at least one verified, available provider
      max_price  base_price <= value
      sort       price_asc | price_desc | name
    """
    query = (request.GET.get('q') or '').strip()[:100]
    category_slug = (request.GET.get('category') or '').strip()
    pincode = (request.GET.get('pincode') or '').strip()
    verified_only = request.GET.get('verified') == '1'
    max_price = _int_or_none(request.GET.get('max_price'))
    sort = (request.GET.get('sort') or '').strip()

    services = (
        Service.objects.filter(is_active=True)
        .select_related('category')
        .annotate(provider_count=Count('offering_providers', distinct=True))
    )
    categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')

    if query:
        services = services.filter(
            Q(name__icontains=query)
            | Q(short_description__icontains=query)
            | Q(detailed_description__icontains=query)
            | Q(category__name__icontains=query)
        )

    if category_slug:
        services = services.filter(category__slug=category_slug)

    if max_price is not None and max_price > 0:
        services = services.filter(base_price__lte=max_price)

    verified_provider_filter = Q(
        offering_providers__provider__is_verified=True,
        offering_providers__provider__is_available_today=True,
        offering_providers__is_active=True,
    )

    if verified_only:
        services = services.filter(verified_provider_filter).distinct()

    if pincode:
        # Providers covering a pincode store it as a comma separated string, so
        # an icontains match is the practical way to filter on SQLite + MySQL.
        services = services.filter(
            verified_provider_filter
            & Q(offering_providers__provider__service_pincodes__icontains=pincode)
        ).distinct()

    if sort == 'price_asc':
        services = services.order_by('base_price')
    elif sort == 'price_desc':
        services = services.order_by('-base_price')
    elif sort == 'name':
        services = services.order_by('name')
    else:
        services = services.order_by('category__display_order', 'base_price')

    paginator = Paginator(services, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'services/list.html', {
        'services': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'querystring': query_params.urlencode(),
        'categories': categories,
        'selected_category': category_slug,
        'query': query,
        'pincode': pincode,
        'verified_only': verified_only,
        'max_price': request.GET.get('max_price', ''),
        'sort': sort,
        'total_results': paginator.count,
        'title': 'Explore Home Services',
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    services = (
        Service.objects.filter(category=category, is_active=True)
        .select_related('category')
        .order_by('base_price')
    )
    categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')

    return render(request, 'services/category_detail.html', {
        'category': category,
        'services': services,
        'categories': categories,
        'title': f'{category.name} Services — HomeBuddy',
    })


def service_detail(request, slug):
    service = get_object_or_404(
        Service.objects.select_related('category'), slug=slug, is_active=True
    )

    provider_mappings = (
        ProviderService.objects.filter(
            service=service, is_active=True,
            provider__is_verified=True,
            provider__is_available_today=True,
        )
        .select_related('provider', 'provider__user')
        .order_by('-provider__avg_rating')
    )

    # Related services in the same category, cheapest first.
    related = (
        Service.objects.filter(category=service.category, is_active=True)
        .exclude(id=service.id)
        .order_by('base_price')[:3]
    )

    return render(request, 'services/service_detail.html', {
        'service': service,
        'provider_mappings': provider_mappings,
        'verified_providers': ProviderProfile.objects.filter(
            is_verified=True, is_available_today=True
        ).order_by('-avg_rating')[:6],
        'related_services': related,
        'title': f'{service.name} — Details & Booking',
    })
