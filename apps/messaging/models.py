from django.db import models
from django.conf import settings
from apps.bookings.models import Booking
from apps.customers.models import CustomerProfile
from apps.professionals.models import ProviderProfile

class Conversation(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='conversation')
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='conversations')
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat for #{self.booking.booking_number} ({self.customer.user.first_name} & {self.provider.business_name})"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.first_name}: {self.content[:30]}"
