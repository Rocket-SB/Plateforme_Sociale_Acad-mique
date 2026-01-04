import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
            self.group_name = f'notifications_{self.user.id}'

            # Rejoindre le groupe de l'utilisateur
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()
            
            # Envoyer le nombre initial de notifications non lues
            await self.send_unread_count()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Gère les messages entrants du client (par ex. pour marquer les notifs comme lues)
        """
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'mark_as_read':
            # Logique pour marquer les notifications comme lues
            await self.mark_notifications_as_read()

    @database_sync_to_async
    def get_unread_notification_count(self):
        return Notification.objects.filter(recipient=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_notifications_as_read(self):
        """Marque toutes les notifications non lues de l'utilisateur comme lues."""
        Notification.objects.filter(recipient=self.user, is_read=False).update(is_read=True)

    async def send_unread_count(self):
        """Envoie le nombre de notifications non lues au client."""
        unread_count = await self.get_unread_notification_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'unread_count': unread_count
        }))

    async def notification_message(self, event):
        """
        Handler pour les messages de notification envoyés au groupe.
        """
        # Envoyer le nouveau compte au client
        await self.send_unread_count()
