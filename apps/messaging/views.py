"""Messaging between customer and technician for a booking."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.bookings.models import Booking
from apps.notifications.services import notify
from .models import Conversation, Message


@login_required
def chat_view(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('customer__user', 'provider__user'), id=booking_id
    )

    is_cust = (
        hasattr(request.user, 'customer_profile')
        and booking.customer_id == request.user.customer_profile.id
    )
    is_prov = (
        hasattr(request.user, 'provider_profile')
        and booking.provider_id == request.user.provider_profile.id
    )
    if not (is_cust or is_prov or request.user.is_admin_user):
        messages.error(request, "You are not authorised to access this conversation.")
        return redirect('core:home')

    if not booking.provider:
        messages.warning(request, "Chat becomes available once a technician is assigned.")
        return redirect('bookings:detail', booking_id=booking.id)

    conversation, _ = Conversation.objects.get_or_create(
        booking=booking,
        defaults={'customer': booking.customer, 'provider': booking.provider},
    )

    if request.method == 'POST':
        content = (request.POST.get('content') or '').strip()
        if not content:
            messages.error(request, "Type a message before sending.")
        elif len(content) > 2000:
            messages.error(request, "Messages are limited to 2000 characters.")
        else:
            Message.objects.create(
                conversation=conversation, sender=request.user, content=content
            )
            conversation.save()  # bumps updated_at

            recipient = (
                booking.provider.user if is_cust else booking.customer.user
            )
            notify(
                recipient,
                "New message",
                f"{request.user.get_full_name() or request.user.username}: {content[:120]}",
                'CHAT',
                f"/messages/booking/{booking.id}/",
            )
            return redirect('messaging:chat', booking_id=booking.id)

    # Mark messages from the other party as read
    conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)

    paginator = Paginator(conversation.messages.select_related('sender'), 50)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'messaging/chat.html', {
        'booking': booking,
        'conversation': conversation,
        'chat_messages': page_obj,
        'page_obj': page_obj,
        'is_customer': is_cust,
        'title': f'Chat — Booking #{booking.booking_number}',
    })
