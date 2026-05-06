import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Chat, Message

class ChatConsumer(AsyncWebsocketConsumer):
    # handler for WebSocket connection
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        self.user = self.scope['user']

        # reject if not authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # reject if user is not part of this chat
        if not await self.is_participant():
            await self.close()
            return

        # accept the connection and add to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    # handler for WebSocket disconnection
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    # handler for messages received from WebSocket clients
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message_text', '').strip()
        if not message_text:
            return

        # save message to DB
        message = await self.save_message(message_text)

        # broadcast to everyone in the chat room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': message.id,
                'message_text': message.message_text,
                'sender_username': self.user.username,
                'is_read': False,
                'created_at': message.created_at.isoformat(),
            }
        )
    # handler for messages sent to the group, helps to send the message to WebSocket clients
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'message_text': event['message_text'],
            'sender_username': event['sender_username'],
            'is_read': event['is_read'],
            'created_at': event['created_at'],
        }))
    # helper method to check if the user is a participant of the chat
    @database_sync_to_async
    def is_participant(self):
        from django.db.models import Q
        return Chat.objects.filter(
            Q(participant1=self.user) | Q(participant2=self.user),
            id=self.chat_id
        ).exists()

    # helper method to save the message to the database
    @database_sync_to_async
    def save_message(self, message_text):
        chat = Chat.objects.get(id=self.chat_id)
        return Message.objects.create(
            chat=chat,
            sender=self.user,
            message_text=message_text
        )