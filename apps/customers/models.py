from django.db import models
from django.conf import settings

class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, null=True, blank=True)
    notes = models.TextField(null=True, blank=True, help_text="Special household notes or entry instructions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer: {self.user.get_full_name() or self.user.username}"


class Address(models.Model):
    TITLE_CHOICES = (
        ('Home', 'Home'),
        ('Office', 'Office'),
        ('Other', 'Other'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=20, choices=TITLE_CHOICES, default='Home')
    address_line1 = models.CharField(max_length=255, verbose_name="House/Flat No, Apartment/Street")
    address_line2 = models.CharField(max_length=255, null=True, blank=True, verbose_name="Area / Locality")
    landmark = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=100, default='Pune')
    state = models.CharField(max_length=100, default='Maharashtra')
    pincode = models.CharField(max_length=10, verbose_name="6-Digit Postal Code")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Customer Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.title}: {self.address_line1}, {self.address_line2 or self.city} ({self.pincode})"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set other addresses for this user to false
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
