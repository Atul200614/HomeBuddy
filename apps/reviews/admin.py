from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'booking', 'provider', 'customer', 'rating', 'is_approved', 'created_at',
    )
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('provider__business_name', 'customer__user__email', 'review_text')
    list_editable = ('is_approved',)
    list_per_page = 25
    readonly_fields = ('created_at',)
    actions = ['approve_reviews', 'hide_reviews']

    def _recalculate(self, queryset):
        for provider in {review.provider for review in queryset.select_related('provider')}:
            provider.update_rating()

    @admin.action(description='Approve reviews (publish)')
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self._recalculate(queryset)
        self.message_user(request, "Selected reviews approved and provider ratings recalculated.")

    @admin.action(description='Hide reviews from public')
    def hide_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self._recalculate(queryset)
        self.message_user(request, "Selected reviews hidden.")
