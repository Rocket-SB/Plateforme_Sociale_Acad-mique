from django import template
from apps.notifications.models import Notification

register = template.Library()

@register.simple_tag
def get_user_notifications(user):
    return Notification.objects.filter(recipient=user).order_by('-created_at')[:5]