"""Model registration for the built-in Django admin (staff CRUD + audit)."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'email', 'full_name', 'phone', 'role', 'is_verified_badge',
        'is_active', 'is_staff', 'date_joined',
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    list_per_page = 25
    readonly_fields = ('date_joined', 'last_login', 'last_login_ip')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Permissions & roles', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Activity', {'fields': ('last_login', 'last_login_ip', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'role',
                       'password1', 'password2'),
        }),
    )
    actions = ['activate_users', 'deactivate_users']

    @admin.display(description='Name')
    def full_name(self, obj):
        return obj.get_full_name() or '—'

    @admin.display(description='Verified', boolean=True)
    def is_verified_badge(self, obj):
        if obj.role != 'PROVIDER':
            return None
        profile = getattr(obj, 'provider_profile', None)
        return bool(profile and profile.is_verified)

    @admin.action(description='Activate selected accounts')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} account(s) activated.")

    @admin.action(description='Suspend selected accounts')
    def deactivate_users(self, request, queryset):
        updated = queryset.exclude(pk=request.user.pk).update(is_active=False)
        self.message_user(request, f"{updated} account(s) suspended.")
