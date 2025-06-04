from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'sender', 'short_message')
    list_filter = ('sender', 'timestamp')
    ordering = ('-timestamp',)

    def short_message(self, obj):
        return obj.message[:75]
    short_message.short_description = 'Message'
