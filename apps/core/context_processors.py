from django.conf import settings

from apps.notifications.models import Notification


def global_context(request):
    """
    Values every template needs. Kept to cheap COUNT queries and guarded so an
    empty database (first run) can never break rendering.
    """
    from apps.bookings.models import Booking
    from apps.services.models import Category

    try:
        nav_categories = list(Category.objects.filter(is_active=True)[:8])
    except Exception:  # database not migrated yet
        nav_categories = []

    unread_notifications = 0
    active_bookings_count = 0

    if hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False):
        try:
            unread_notifications = Notification.objects.filter(
                user=request.user, is_read=False
            ).count()

            if request.user.is_customer:
                profile = getattr(request.user, 'customer_profile', None)
                if profile:
                    active_bookings_count = Booking.objects.filter(
                        customer=profile,
                        status__in=[
                            'REQUESTED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED',
                            'IN_PROGRESS', 'WORK_PROOF_SUBMITTED',
                        ],
                    ).count()
            elif request.user.is_provider:
                profile = getattr(request.user, 'provider_profile', None)
                if profile:
                    active_bookings_count = Booking.objects.filter(
                        provider=profile,
                        status__in=[
                            'REQUESTED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED',
                            'IN_PROGRESS',
                        ],
                    ).count()
        except Exception:
            unread_notifications = 0
            active_bookings_count = 0

    return {
        'nav_categories': nav_categories,
        'unread_notifications_count': unread_notifications,
        'active_bookings_count': active_bookings_count,
        'default_city': 'Pune, Maharashtra',
        'platform_name': 'HomeBuddy',
        'support_phone': '+91 79711 23101',
        'razorpay_demo_mode': getattr(settings, 'RAZORPAY_DEMO_MODE', True),
        'platform_commission_rate': getattr(settings, 'PLATFORM_COMMISSION_RATE', 10),
    }
