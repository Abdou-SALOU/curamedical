from django.contrib import admin
from .models import WhatsAppConversation, WhatsAppMessage


class WhatsAppMessageInline(admin.TabularInline):
    model = WhatsAppMessage
    extra = 0
    readonly_fields = ('direction', 'body', 'media_url', 'twilio_sid', 'sent_at')
    can_delete = False


@admin.register(WhatsAppConversation)
class WhatsAppConversationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'patient', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('phone_number', 'patient__nom', 'patient__prenom')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WhatsAppMessageInline]


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'direction', 'body_preview', 'sent_at')
    list_filter = ('direction', 'sent_at')
    readonly_fields = ('sent_at',)

    def body_preview(self, obj):
        return obj.body[:80]
    body_preview.short_description = 'Message'
