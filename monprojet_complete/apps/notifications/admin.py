from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(SimpleHistoryAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at', 'recipient']
    search_fields = ['title', 'message', 'recipient__username', 'sender__username']
    readonly_fields = ['created_at', 'read_at']
    
    def get_queryset(self, request):
        """Limiter l'affichage selon les permissions"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Les non-superusers ne voient que leurs propres notifications
        return qs.filter(recipient=request.user)

