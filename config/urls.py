"""
HomeBuddy URL Configuration
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.sitemaps import CategorySitemap, ServiceSitemap, StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'services': ServiceSitemap,
}

urlpatterns = [
    # Django built-in admin (full model CRUD for staff)
    path('django-admin/', admin.site.urls),

    # Core public pages
    path('', include('apps.core.urls')),

    # Authentication
    path('accounts/', include('apps.accounts.urls')),

    # Customer portal
    path('customer/', include('apps.customers.urls')),

    # Professional / technician portal
    path('provider/', include('apps.professionals.urls')),

    # Services catalogue
    path('services/', include('apps.services.urls')),

    # Booking engine
    path('bookings/', include('apps.bookings.urls')),

    # Payments, invoices, Razorpay webhook
    path('payments/', include('apps.payments.urls')),

    # Reviews
    path('reviews/', include('apps.reviews.urls')),

    # Complaints & disputes
    path('complaints/', include('apps.complaints.urls')),

    # Messaging
    path('messages/', include('apps.messaging.urls')),

    # Notifications
    path('notifications/', include('apps.notifications.urls')),

    # Custom admin operations dashboard
    path('admin-panel/', include('apps.admin_dashboard.urls')),

    # REST API (React + Vite frontend)
    path('api/v1/auth/', include('apps.accounts.api_urls')),
    path('api/v1/services/', include('apps.services.api_urls')),
    path('api/v1/bookings/', include('apps.bookings.api_urls')),
    path('api/v1/payments/', include('apps.payments.api_urls')),

    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler400 = 'apps.core.views.error_400'
handler403 = 'apps.core.views.error_403'
handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'

# Admin branding
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'HomeBuddy Administration')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'HomeBuddy Admin')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Marketplace Operations')
