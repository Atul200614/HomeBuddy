from django.db import models
from django.utils.text import slugify
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    icon_name = models.CharField(max_length=50, default='bi-tools', help_text="Bootstrap Icon name e.g. bi-droplet, bi-lightning, bi-brush")
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Service Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    PRICING_TYPES = (
        ('FIXED', 'Fixed Package Rate'),
        ('HOURLY', 'Hourly Labor Rate'),
        ('PACKAGE', 'Comprehensive BHK Package'),
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=150, verbose_name="Service Name")
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    short_description = models.CharField(max_length=255, help_text="Short teaser description for service cards")
    detailed_description = models.TextField(help_text="Full service inclusions, exclusions, and warranty notes")
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPES, default='FIXED')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Base Price (₹)")
    estimated_duration_minutes = models.PositiveIntegerField(default=60, help_text="Estimated time in minutes")
    
    is_emergency_eligible = models.BooleanField(default=False, verbose_name="Emergency Booking Allowed")
    emergency_surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('199.00'), verbose_name="Emergency Surcharge (₹)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'base_price']

    def __str__(self):
        return f"{self.name} (Starts at ₹{self.base_price})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProviderService(models.Model):
    from apps.professionals.models import ProviderProfile
    provider = models.ForeignKey('professionals.ProviderProfile', on_delete=models.CASCADE, related_name='provided_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='offering_providers')
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Leave blank to use base catalog price")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('provider', 'service')

    def __str__(self):
        return f"{self.provider.business_name} - {self.service.name}"

    @property
    def effective_price(self):
        return self.custom_price if self.custom_price is not None else self.service.base_price
