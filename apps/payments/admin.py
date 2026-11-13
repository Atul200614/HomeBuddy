from django.contrib import admin

from .models import EarningsLedger, Invoice, Payment, PayoutRequest


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'booking', 'amount', 'payment_method', 'status', 'is_demo',
        'cash_received_by_provider', 'paid_at', 'created_at',
    )
    list_filter = ('status', 'payment_method', 'is_demo', 'created_at')
    search_fields = (
        'booking__booking_number', 'razorpay_payment_id',
        'razorpay_order_id', 'booking__customer__user__email',
    )
    date_hierarchy = 'created_at'
    list_per_page = 25
    readonly_fields = (
        'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature',
        'razorpay_refund_id', 'gateway_response', 'created_at', 'updated_at',
    )
    list_select_related = ('booking',)


@admin.register(EarningsLedger)
class EarningsLedgerAdmin(admin.ModelAdmin):
    list_display = (
        'provider', 'booking', 'gross_amount', 'commission_rate',
        'commission_amount', 'net_earnings', 'is_paid_out', 'created_at',
    )
    list_filter = ('is_paid_out', 'created_at')
    search_fields = ('provider__business_name', 'booking__booking_number')
    list_editable = ('is_paid_out',)
    list_per_page = 25


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'provider', 'amount', 'masked_account_display', 'status',
        'requested_at', 'processed_at',
    )
    list_filter = ('status', 'requested_at')
    search_fields = ('provider__business_name', 'bank_account_name', 'admin_reference')
    readonly_fields = ('requested_at',)
    list_per_page = 25

    @admin.display(description='Account')
    def masked_account_display(self, obj):
        return obj.masked_account


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'booking', 'subtotal', 'tax_amount', 'total_amount', 'created_at')
    search_fields = ('invoice_number', 'booking__booking_number')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
