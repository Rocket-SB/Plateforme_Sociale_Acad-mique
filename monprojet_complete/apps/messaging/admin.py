from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(SimpleHistoryAdmin):
    list_display = ['id', 'participants_list', 'created_at', 'updated_at']
    filter_horizontal = ['participants']
    readonly_fields = ['created_at', 'updated_at']
    
    def participants_list(self, obj):
        return ', '.join([p.username for p in obj.participants.all()])
    participants_list.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(SimpleHistoryAdmin):
    list_display = ['sender', 'recipient', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__username', 'recipient__username']
    readonly_fields = ['created_at', 'read_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Contenu'

