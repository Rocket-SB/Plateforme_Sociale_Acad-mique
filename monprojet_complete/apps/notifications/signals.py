from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

@receiver(post_save, sender=Notification)
def notification_created_handler(sender, instance, created, **kwargs):
    """
    Envoie une notification via WebSocket lorsqu'une nouvelle notification est créée.
    """
    if created:
        channel_layer = get_channel_layer()
        user_id = instance.recipient.id
        group_name = f'notifications_{user_id}'

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification_message',
                'message': {
                    'id': instance.id,
                    'title': instance.title,
                    'message': instance.message,
                    'created_at': instance.created_at.isoformat(),
                }
            }
        )
