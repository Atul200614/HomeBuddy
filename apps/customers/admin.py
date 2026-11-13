from django.contrib import admin

from .models import Address, CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'emergency_contact_name', 'emergency_contact_phone', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'emergency_contact_phone')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'address_line1', 'address_line2', 'city', 'pincode', 'is_default')
    list_filter = ('title', 'city', 'is_default')
    search_fields = ('user__email', 'address_line1', 'address_line2', 'pincode')
    list_per_page = 25
