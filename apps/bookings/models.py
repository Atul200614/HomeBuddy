import uuid
from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.customers.models import CustomerProfile, Address
from apps.professionals.models import ProviderProfile
from apps.services.models import Service

def generate_booking_number():
    return f"HB-{uuid.uuid4().hex[:8].upper()}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('REQUESTED', 'Booking Requested'),
        ('ACCEPTED', 'Accepted by Provider'),
        ('REJECTED', 'Declined by Provider'),
        ('EN_ROUTE', 'Provider En Route'),
        ('ARRIVED', 'Provider Arrived at Location'),
        ('IN_PROGRESS', 'Service in Progress'),
        ('WORK_PROOF_SUBMITTED', 'Work Proof Submitted (Awaiting Customer Sign-off)'),
        ('COMPLETED', 'Service Completed'),
        ('CANCELLED', 'Cancelled'),
        ('DISPUTED', 'Disputed / Under Investigation'),
    )

    TIME_SLOT_CHOICES = (
        ('08:00 AM - 10:00 AM', 'Morning (08:00 AM - 10:00 AM)'),
        ('10:00 AM - 12:00 PM', 'Late Morning (10:00 AM - 12:00 PM)'),
        ('12:00 PM - 02:00 PM', 'Afternoon (12:00 PM - 02:00 PM)'),
        ('02:00 PM - 04:00 PM', 'Late Afternoon (02:00 PM - 04:00 PM)'),
        ('04:00 PM - 06:00 PM', 'Evening (04:00 PM - 06:00 PM)'),
        ('06:00 PM - 08:00 PM', 'Late Evening (06:00 PM - 08:00 PM)'),
    )

    booking_number = models.CharField(max_length=32, unique=True, default=generate_booking_number, editable=False)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.PROTECT, related_name='bookings')
    provider = models.ForeignKey(ProviderProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='bookings')
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='service_bookings')

    scheduled_date = models.DateField()
    time_slot = models.CharField(max_length=50, choices=TIME_SLOT_CHOICES, default='10:00 AM - 12:00 PM')
    is_emergency = models.BooleanField(default=False, verbose_name="Emergency Express Dispatch")
    special_instructions = models.TextField(null=True, blank=True, help_text="Specific issues, flat directions, access gates")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='REQUESTED')
    rejection_reason = models.TextField(null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)

    service_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    emergency_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking_number} — {self.service.name} ({self.get_status_display()})"

    def calculate_total(self):
        self.total_amount = max(Decimal('0.00'), (self.service_price + self.emergency_fee - self.discount_amount))
        return self.total_amount

    def is_in_active_state(self):
        return self.status in ['REQUESTED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED', 'IN_PROGRESS', 'WORK_PROOF_SUBMITTED']


class BookingStatusHistory(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=30, null=True, blank=True)
    to_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.booking.booking_number}: {self.from_status} -> {self.to_status}"


class WorkProof(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='work_proof')
    before_photo = models.ImageField(upload_to='work_proofs/before/')
    after_photo = models.ImageField(upload_to='work_proofs/after/')
    work_notes = models.TextField(help_text="Detailed notes describing steps taken, parts replaced, or cleaning results")
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    customer_confirmed = models.BooleanField(default=False, verbose_name="Customer Approved Work")
    customer_confirmed_at = models.DateTimeField(null=True, blank=True)
    customer_feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        status = "Confirmed" if self.customer_confirmed else "Pending Sign-off"
        return f"Work Proof for {self.booking.booking_number} [{status}]"
