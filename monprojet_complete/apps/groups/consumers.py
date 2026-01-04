import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Groupe, GroupMessage

User = get_user_model()

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_name = f'group_{self.group_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        is_member = await self.is_member(self.user, self.group_id)
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']

        if not message_content:
            return

        message = await self.create_message(message_content)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender': self.user.get_full_name() or self.user.username,
                'sender_id': self.user.id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id']
        }))

    @database_sync_to_async
    def is_member(self, user, group_id):
        group = Groupe.objects.get(id=group_id)
        return group.members.filter(id=user.id).exists()

    @database_sync_to_async
    def create_message(self, message):
        group = Groupe.objects.get(id=self.group_id)
        return GroupMessage.objects.create(
            group=group,
            sender=self.user,
            content=message
        )
