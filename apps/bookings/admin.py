from django.contrib import admin

from .models import Booking, BookingStatusHistory, WorkProof


class BookingStatusHistoryInline(admin.TabularInline):
    model = BookingStatusHistory
    extra = 0
    fields = ('from_status', 'to_status', 'changed_by', 'notes', 'created_at')
    readonly_fields = ('from_status', 'to_status', 'changed_by', 'notes', 'created_at')
    can_delete = False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_number', 'customer', 'provider', 'service', 'scheduled_date',
        'time_slot', 'status', 'total_amount', 'is_emergency', 'created_at',
    )
    list_filter = ('status', 'is_emergency', 'scheduled_date', 'time_slot')
    search_fields = (
        'booking_number', 'customer__user__email', 'customer__user__phone',
        'provider__business_name', 'service__name',
    )
    date_hierarchy = 'scheduled_date'
    list_per_page = 25
    readonly_fields = ('booking_number', 'created_at', 'updated_at')
    inlines = [BookingStatusHistoryInline]
    list_select_related = ('customer__user', 'provider', 'service')
    actions = ['mark_cancelled']

    @admin.action(description='Cancel selected bookings')
    def mark_cancelled(self, request, queryset):
        updated = queryset.exclude(status__in=['COMPLETED', 'CANCELLED']).update(
            status='CANCELLED', cancellation_reason='Cancelled by administrator'
        )
        self.message_user(request, f"{updated} booking(s) cancelled.")


@admin.register(BookingStatusHistory)
class BookingStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'from_status', 'to_status', 'changed_by', 'created_at')
    list_filter = ('to_status', 'created_at')
    search_fields = ('booking__booking_number', 'notes')


@admin.register(WorkProof)
class WorkProofAdmin(admin.ModelAdmin):
    list_display = (
        'booking', 'customer_confirmed', 'submitted_at', 'customer_confirmed_at',
    )
    list_filter = ('customer_confirmed', 'submitted_at')
    search_fields = ('booking__booking_number', 'work_notes')
    readonly_fields = ('submitted_at', 'customer_confirmed_at')
