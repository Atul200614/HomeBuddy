from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ('sender', 'content', 'is_read', 'created_at')
    readonly_fields = ('sender', 'content', 'created_at')
    can_delete = False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('booking', 'customer', 'provider', 'message_count', 'created_at', 'updated_at')
    search_fields = ('booking__booking_number', 'customer__user__email', 'provider__business_name')
    inlines = [MessageInline]
    list_select_related = ('booking', 'customer__user', 'provider')

    @admin.display(description='Messages')
    def message_count(self, obj):
        return obj.messages.count()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'short_content', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__email', 'conversation__booking__booking_number')

    @admin.display(description='Message')
    def short_content(self, obj):
        return obj.content[:60] + ('…' if len(obj.content) > 60 else '')
