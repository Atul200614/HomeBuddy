"""Public pages: home, static content, error handlers, sitemap support."""
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import render

from apps.professionals.models import ProviderProfile
from apps.reviews.models import Review
from apps.services.models import Category, Service


def home(request):
    """Landing page. Cached for 5 minutes because it is fully public."""
    cache_key = 'home_page_context_v2'
    context = cache.get(cache_key)

    if context is None:
        categories = (
            Category.objects.filter(is_active=True)
            .annotate(service_count=Count('services', filter=Q(services__is_active=True)))
            .order_by('display_order', 'name')[:8]
        )
        featured_services = (
            Service.objects.filter(is_active=True)
            .select_related('category')
            .order_by('base_price')[:8]
        )
        verified_providers = (
            ProviderProfile.objects.filter(is_verified=True, is_available_today=True)
            .select_related('user')
            .order_by('-avg_rating', '-total_jobs_completed')[:4]
        )
        customer_reviews = (
            Review.objects.filter(is_approved=True)
            .select_related('customer__user', 'provider')
            .order_by('-created_at')[:4]
        )
        context = {
            'categories': list(categories),
            'featured_services': list(featured_services),
            'verified_providers': list(verified_providers),
            'customer_reviews': list(customer_reviews),
        }
        cache.set(cache_key, context, 300)

    context = dict(context)
    context['title'] = 'HomeBuddy — Certified Home Services & Repairs Marketplace'
    return render(request, 'public/index.html', context)


def about(request):
    return render(request, 'public/about.html', {'title': 'About HomeBuddy'})


def faq(request):
    return render(request, 'public/faq.html', {'title': 'Frequently Asked Questions'})


def contact(request):
    return render(request, 'public/contact.html', {'title': 'Customer Support & Helpdesk'})


def terms(request):
    return render(request, 'public/terms.html', {'title': 'Terms and Conditions'})


def privacy(request):
    return render(request, 'public/privacy.html', {'title': 'Privacy Policy'})


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
def error_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)


def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
