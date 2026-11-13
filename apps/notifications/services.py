"""
Notification helpers.

Every important domain event funnels through :func:`notify` so the bell badge,
the notifications page and the audit trail stay consistent. Email delivery is
best-effort and never breaks the calling transaction.
"""
import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import Notification

logger = logging.getLogger('homebuddy.notifications')


def notify(user, title, message, notification_type='SYSTEM', link_url=None, email=False):
    """Create an in-app notification (and optionally an email). Returns it."""
    if user is None:
        return None

    notification = Notification.objects.create(
        user=user,
        title=title[:150],
        message=message,
        notification_type=notification_type,
        link_url=link_url,
    )

    if email and user.email:
        try:
            send_mail(
                subject=f"[HomeBuddy] {title}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:  # pragma: no cover - email must never break a request
            logger.exception("Notification email failed for %s", user.email)

    return notification


def notify_many(users, title, message, notification_type='SYSTEM', link_url=None):
    """Notify an iterable of users (duplicates are ignored)."""
    created = []
    seen = set()
    for user in users:
        if user is None or user.pk in seen:
            continue
        seen.add(user.pk)
        created.append(notify(user, title, message, notification_type, link_url))
    return created
