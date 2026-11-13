from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.bookings.models import Booking
from apps.customers.models import CustomerProfile
from apps.professionals.models import ProviderProfile

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='reviews')
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Star rating from 1 to 5"
    )
    review_text = models.TextField(verbose_name="Your Experience & Comments")
    is_approved = models.BooleanField(default=True, verbose_name="Approved for Public Display")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}★ Review for {self.provider.business_name} by {self.customer.user.get_full_name()}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate provider average rating immediately
        self.provider.update_rating()
