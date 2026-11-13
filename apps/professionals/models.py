from django.db import models
from django.conf import settings
from decimal import Decimal

class ProviderProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_profile')
    business_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Business / Trade Name")
    bio = models.TextField(null=True, blank=True, help_text="Short description of your services, expertise, and standards")
    experience_years = models.PositiveIntegerField(default=2, verbose_name="Years of Experience")
    is_verified = models.BooleanField(default=False, verbose_name="KYC Verified Badge")
    verification_date = models.DateTimeField(null=True, blank=True)
    
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('5.00'), verbose_name="Average Rating")
    total_reviews = models.PositiveIntegerField(default=0)
    total_jobs_completed = models.PositiveIntegerField(default=0)
    
    service_city = models.CharField(max_length=100, default='Pune')
    service_pincodes = models.TextField(default='411038, 411045, 411057, 411014', help_text="Comma-separated postal codes serviced")
    is_available_today = models.BooleanField(default=True, verbose_name="Available for Jobs Today")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('299.00'), verbose_name="Standard Hourly Rate (₹)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Provider Profile'
        verbose_name_plural = 'Provider Profiles'
        ordering = ['-is_verified', '-avg_rating']

    def __str__(self):
        status = "Verified" if self.is_verified else "Unverified"
        return f"{self.business_name or self.user.get_full_name()} [{status}]"

    def update_rating(self):
        """Recalculate provider average rating from approved customer reviews."""
        from apps.reviews.models import Review
        reviews = Review.objects.filter(provider=self, is_approved=True)
        count = reviews.count()
        if count > 0:
            total = sum(r.rating for r in reviews)
            self.avg_rating = round(Decimal(total) / Decimal(count), 2)
            self.total_reviews = count
        else:
            self.avg_rating = Decimal('5.00')
            self.total_reviews = 0
        self.save(update_fields=['avg_rating', 'total_reviews'])


class VerificationDocument(models.Model):
    DOCUMENT_TYPES = (
        ('AADHAAR', 'Aadhaar Card (National ID)'),
        ('PAN', 'PAN Card (Tax ID)'),
        ('POLICE_VERIFICATION', 'Police Clearance Certificate'),
        ('SKILL_CERTIFICATE', 'Trade Certification / Diploma'),
        ('DRIVING_LICENSE', 'Driving License / ID'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Under Review'),
        ('APPROVED', 'Verified & Approved'),
        ('REJECTED', 'Rejected'),
    )
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='kyc_documents/', verbose_name="Document Image / PDF")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(null=True, blank=True, help_text="Reason for rejection or verification remarks")
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.provider.user.get_full_name()} ({self.get_status_display()})"


class ProviderSkill(models.Model):
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=100, verbose_name="Trade / Skill Name")
    years_experience = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.skill_name} ({self.years_experience} yrs) - {self.provider.business_name}"


class ProviderAvailability(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField(default='09:00:00')
    end_time = models.TimeField(default='18:00:00')
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('provider', 'day_of_week')
        ordering = ['day_of_week']

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.start_time} - {self.end_time}"
