from django.contrib import admin

from .models import Category, ProviderService, Service


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_name', 'display_order', 'service_count', 'is_active')
    list_editable = ('display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='Services')
    def service_count(self, obj):
        return obj.services.filter(is_active=True).count()


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'pricing_type', 'base_price', 'estimated_duration_minutes',
        'is_emergency_eligible', 'emergency_surcharge', 'is_active',
    )
    list_filter = ('category', 'pricing_type', 'is_emergency_eligible', 'is_active')
    search_fields = ('name', 'short_description', 'detailed_description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('base_price', 'is_active')
    list_per_page = 25


@admin.register(ProviderService)
class ProviderServiceAdmin(admin.ModelAdmin):
    list_display = ('provider', 'service', 'custom_price', 'effective_price_display', 'is_active')
    list_filter = ('service__category', 'is_active')
    search_fields = ('provider__business_name', 'service__name')
    list_select_related = ('provider', 'service')

    @admin.display(description='Effective price')
    def effective_price_display(self, obj):
        return f"₹{obj.effective_price}"
