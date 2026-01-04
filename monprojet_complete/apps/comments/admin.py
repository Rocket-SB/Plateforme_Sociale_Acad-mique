from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Commentaire


@admin.register(Commentaire)
class CommentaireAdmin(SimpleHistoryAdmin):
    list_display = ['author', 'content_preview', 'parent', 'like_count', 'created_at']
    list_filter = ['created_at', 'is_edited']
    search_fields = ['content', 'author__username']
    readonly_fields = ['created_at', 'updated_at', 'like_count']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Contenu'

