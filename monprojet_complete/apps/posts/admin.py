from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Post


@admin.register(Post)
class PostAdmin(SimpleHistoryAdmin):
    list_display = ['author', 'group', 'content_preview', 'like_count', 'comment_count', 'created_at']
    list_filter = ['created_at', 'group']
    search_fields = ['content', 'author__username']
    readonly_fields = ['created_at', 'updated_at', 'like_count', 'comment_count', 'share_count']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Contenu'

