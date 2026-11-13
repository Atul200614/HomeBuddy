from decimal import Decimal

from django.db import models

from apps.bookings.models import Booking
from apps.professionals.models import ProviderProfile


class Payment(models.Model):
    METHOD_CHOICES = (
        ('ONLINE_RAZORPAY', 'Online Payment (UPI, Cards, NetBanking via Razorpay)'),
        ('CASH', 'Cash on Service (Pay technician after completion)'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Payment Pending'),
        ('SUCCESS', 'Payment Successful'),
        ('FAILED', 'Payment Failed'),
        ('REFUNDED', 'Refunded'),
    )

    booking = models.OneToOneField(Booking, on_delete=models.PROTECT, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=METHOD_CHOICES, default='ONLINE_RAZORPAY')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    razorpay_refund_id = models.CharField(max_length=100, null=True, blank=True)

    # True when the payment was completed through the clearly-labelled demo
    # simulator instead of the real Razorpay gateway.
    is_demo = models.BooleanField(default=False, verbose_name="Simulated (Demo) Payment")
    failure_reason = models.CharField(max_length=255, null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)

    cash_received_by_provider = models.BooleanField(default=False, verbose_name="Technician Received Cash")
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status', 'payment_method'])]

    def __str__(self):
        return f"Payment #{self.id} — {self.booking.booking_number} (₹{self.amount}) [{self.status}]"

    @property
    def is_settled(self):
        """Money has actually been collected for this booking."""
        if self.status != 'SUCCESS':
            return False
        if self.payment_method == 'CASH':
            return self.cash_received_by_provider
        return True


class EarningsLedger(models.Model):
    provider = models.ForeignKey(ProviderProfile, on_delete=models.PROTECT, related_name='earnings_ledger')
    booking = models.OneToOneField(Booking, on_delete=models.PROTECT, related_name='earnings_record')
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('10.00'),
        help_text="HomeBuddy platform fee percentage",
    )
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ledger #{self.id} — {self.provider.business_name} (+₹{self.net_earnings})"


class PayoutRequest(models.Model):
    STATUS_CHOICES = (
        ('REQUESTED', 'Requested by Technician'),
        ('APPROVED', 'Approved by Finance Admin'),
        ('REJECTED', 'Rejected'),
        ('TRANSFERRED', 'Settled & Transferred'),
    )
    provider = models.ForeignKey(ProviderProfile, on_delete=models.PROTECT, related_name='payout_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bank_account_name = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=30)
    bank_ifsc = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    admin_reference = models.CharField(max_length=100, null=True, blank=True, help_text="Bank NEFT / IMPS reference")
    admin_notes = models.TextField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Payout Request #{self.id} — ₹{self.amount} ({self.get_status_display()})"

    @property
    def masked_account(self):
        if not self.bank_account_number:
            return '—'
        return f"{'*' * max(len(self.bank_account_number) - 4, 0)}{self.bank_account_number[-4:]}"


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=40, unique=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='invoice')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} (₹{self.total_amount})"
