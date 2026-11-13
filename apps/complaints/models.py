import uuid
from django.db import models
from django.conf import settings
from apps.bookings.models import Booking

def generate_complaint_number():
    return f"CMP-{uuid.uuid4().hex[:6].upper()}"

class Complaint(models.Model):
    CATEGORY_CHOICES = (
        ('POOR_QUALITY', 'Poor Service Quality / Incomplete Work'),
        ('DAMAGE', 'Property Damage or Broken Fixtures'),
        ('NO_SHOW', 'Technician Did Not Arrive (No Show)'),
        ('OVERCHARGING', 'Technician Demanded Additional Unauthorized Cash'),
        ('BEHAVIOR', 'Unprofessional Conduct / Rudeness'),
        ('OTHER', 'Other Platform Dispute'),
    )
    STATUS_CHOICES = (
        ('OPEN', 'Ticket Raised (Pending Review)'),
        ('INVESTIGATING', 'Under Investigation by Support'),
        ('RESOLVED', 'Resolved & Settled'),
        ('CLOSED', 'Closed'),
    )

    complaint_number = models.CharField(max_length=32, unique=True, default=generate_complaint_number, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='complaints')
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='raised_complaints')
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='POOR_QUALITY')
    description = models.TextField(verbose_name="Detailed Description of the Issue")
    evidence_file = models.FileField(upload_to='complaints/', null=True, blank=True, verbose_name="Attach Photo or Document Evidence")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    admin_resolution = models.TextField(null=True, blank=True, verbose_name="Support Team Resolution Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.complaint_number} — {self.get_category_display()} [{self.get_status_display()}]"
