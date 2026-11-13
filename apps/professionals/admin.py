from django.contrib import admin
from django.utils import timezone

from .models import ProviderAvailability, ProviderProfile, ProviderSkill, VerificationDocument


class VerificationDocumentInline(admin.TabularInline):
    model = VerificationDocument
    extra = 0
    fields = ('document_type', 'document_file', 'status', 'admin_notes', 'reviewed_at')
    readonly_fields = ('reviewed_at',)


class ProviderSkillInline(admin.TabularInline):
    model = ProviderSkill
    extra = 1


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = (
        'business_name', 'user', 'is_verified', 'avg_rating', 'total_reviews',
        'total_jobs_completed', 'service_city', 'is_available_today',
    )
    list_filter = ('is_verified', 'is_available_today', 'service_city', 'experience_years')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'business_name', 'service_pincodes',
    )
    list_editable = ('is_verified', 'is_available_today')
    list_per_page = 25
    readonly_fields = ('avg_rating', 'total_reviews', 'total_jobs_completed',
                       'created_at', 'updated_at')
    inlines = [VerificationDocumentInline, ProviderSkillInline]
    actions = ['approve_verification', 'revoke_verification', 'mark_available', 'mark_unavailable']

    @admin.action(description='Approve KYC & award Verified badge')
    def approve_verification(self, request, queryset):
        updated = queryset.update(is_verified=True, verification_date=timezone.now())
        self.message_user(request, f"{updated} provider(s) marked KYC Verified.")

    @admin.action(description='Revoke Verified badge')
    def revoke_verification(self, request, queryset):
        updated = queryset.update(is_verified=False, verification_date=None)
        self.message_user(request, f"Verified badge revoked for {updated} provider(s).")

    @admin.action(description='Mark available for jobs today')
    def mark_available(self, request, queryset):
        updated = queryset.update(is_available_today=True)
        self.message_user(request, f"{updated} provider(s) marked available.")

    @admin.action(description='Mark unavailable today')
    def mark_unavailable(self, request, queryset):
        updated = queryset.update(is_available_today=False)
        self.message_user(request, f"{updated} provider(s) marked unavailable.")


@admin.register(VerificationDocument)
class VerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ('provider', 'document_type', 'status', 'submitted_at', 'reviewed_at', 'file_link')
    list_filter = ('status', 'document_type', 'submitted_at')
    search_fields = ('provider__user__email', 'provider__business_name', 'admin_notes')
    list_editable = ('status',)
    list_per_page = 25
    date_hierarchy = 'submitted_at'
    actions = ['approve_documents', 'reject_documents']

    @admin.display(description='File')
    def file_link(self, obj):
        if obj.document_file:
            return format_html('<a href="{}" target="_blank" rel="noopener">Open</a>',
                               obj.document_file.url)
        return '—'

    @admin.action(description='Approve selected documents')
    def approve_documents(self, request, queryset):
        updated = queryset.update(status='APPROVED', reviewed_at=timezone.now())
        self.message_user(request, f"{updated} document(s) approved.")

    @admin.action(description='Reject selected documents')
    def reject_documents(self, request, queryset):
        updated = queryset.update(status='REJECTED', reviewed_at=timezone.now())
        self.message_user(request, f"{updated} document(s) rejected.")


@admin.register(ProviderSkill)
class ProviderSkillAdmin(admin.ModelAdmin):
    list_display = ('provider', 'skill_name', 'years_experience')
    list_filter = ('skill_name',)
    search_fields = ('provider__business_name', 'skill_name')


@admin.register(ProviderAvailability)
class ProviderAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('provider', 'day_of_week', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available')
    search_fields = ('provider__business_name',)
