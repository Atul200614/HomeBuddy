from django.contrib import admin

from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'complaint_number', 'booking', 'raised_by', 'category', 'status',
        'has_evidence', 'created_at',
    )
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('complaint_number', 'booking__booking_number', 'raised_by__email', 'description')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    readonly_fields = ('complaint_number', 'created_at', 'updated_at')

    @admin.display(description='Evidence', boolean=True)
    def has_evidence(self, obj):
        return bool(obj.evidence_file)
