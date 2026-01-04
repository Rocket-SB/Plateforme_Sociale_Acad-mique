from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
        return {
            'unread_count': unread_count,
            'notifications': recent_notifications
        }
    return {}
