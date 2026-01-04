import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
import base64
import uuid

from apps.messaging.models import Message, Conversation
from apps.users.models import Utilisateur
from apps.notifications.utils import notify_new_message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get('message')
        sender_id = text_data_json['sender_id']
        file_data = text_data_json.get('file')
        filename = text_data_json.get('filename')
        
        sender = await self.get_user(sender_id)
        conversation = await self.get_conversation(self.conversation_id)
        
        # Create new message
        message, recipient = await self.create_message(conversation, sender, message_content, file_data, filename)

        # Notify recipient
        if recipient and message:
            await self.notify_recipient(conversation, sender, recipient, message)
            
        file_url = message.file.url if message and message.file else None

        # Send message to room group
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'message': message.content if message else message_content,
                'sender_id': sender.id,
                'sender_username': sender.username,
                'created_at': message.created_at.isoformat() if message else '',
                'file_url': file_url
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event.get('message'),
            'sender_id': event.get('sender_id'),
            'sender_username': event.get('sender_username'),
            'created_at': event.get('created_at'),
            'file_url': event.get('file_url'),
        }))

    @sync_to_async
    def get_user(self, user_id):
        return Utilisateur.objects.get(id=user_id)

    @sync_to_async
    def get_conversation(self, conversation_id):
        return Conversation.objects.get(id=conversation_id)
    
    @sync_to_async
    def create_message(self, conversation, sender, content, file_data=None, filename=None):
        participants = conversation.participants.all()
        recipient = participants.exclude(id=sender.id).first()
        
        if recipient:
            message = Message(
                conversation=conversation,
                sender=sender,
                recipient=recipient, 
                content=content
            )
            if file_data and filename:
                try:
                    data = base64.b64decode(file_data.split(',')[1])
                    ext = filename.split('.')[-1]
                    unique_filename = f"{uuid.uuid4()}.{ext}"
                    message.file.save(unique_filename, ContentFile(data), save=False)
                except Exception as e:
                    print(f"Error decoding or saving file: {e}")
            
            if message.content or message.file:
                message.save()
                return message, recipient
        return None, None

    @sync_to_async
    def notify_recipient(self, conversation, sender, recipient, message):
        notify_new_message(conversation, sender, recipient, message)

