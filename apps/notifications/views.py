from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    unread_only = request.GET.get('unread') == '1'
    if unread_only:
        notifications = notifications.filter(is_read=False)

    paginator = Paginator(notifications, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'notifications/list.html', {
        'notifications': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'unread_only': unread_only,
        'title': 'Your Notifications',
    })


@login_required
@require_POST
def mark_read(request, notification_id):
    """POST-only: reading a notification changes state."""
    notif = get_object_or_404(Notification, id=notification_id, user=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.save(update_fields=['is_read'])

    if notif.link_url and url_has_allowed_host_and_scheme(
        notif.link_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(notif.link_url)
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    updated = Notification.objects.filter(
        user=request.user, is_read=False
    ).update(is_read=True)
    if updated:
        messages.success(request, f"{updated} notification(s) marked as read.")
    return redirect('notifications:list')
