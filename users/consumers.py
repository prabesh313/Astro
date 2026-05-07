import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message


SIGNALING_TYPES = {'call_offer', 'call_answer', 'ice_candidate', 'call_end', 'call_reject', 'call_request'}

class ChatConsumer(AsyncWebsocketConsumer):
    #helps in handling WebSocket connections for chat rooms, including authentication, message handling, and WebRTC signaling
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        if not await self.is_participant():
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    #helps in handling the disconnection of a WebSocket connection from a chat room
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    #helps in handling incoming WebSocket messages, distinguishing between chat messages and WebRTC signaling events, and processing them accordingly
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get('type')

        if msg_type == 'chat_message':
            await self._handle_chat_message(data)

        elif msg_type in SIGNALING_TYPES:
            await self._handle_signaling(data)

    #helps in processing incoming chat messages, saving them to the database, and broadcasting them to all participants in the chat room
    async def _handle_chat_message(self, data):
        message_text = data.get('message_text', '').strip()
        if not message_text:
            return

        message = await self.save_message(message_text)

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

    #helps in handling WebRTC signaling events, relaying them to the chat room group with sender identity
    async def _handle_signaling(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {**data, 'sender_username': self.user.username}
        )

    #helps in sending chat messages to WebSocket clients when a 'chat_message' event is received from the channel layer group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))


    async def call_offer(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_answer(self, event):
        await self.send(text_data=json.dumps(event))

    async def ice_candidate(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_end(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_reject(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_request(self, event):
        await self.send(text_data=json.dumps(event))

    #helps in checking if the authenticated user is a participant in the chat room, allowing or denying access accordingly
    @database_sync_to_async
    def is_participant(self):
        from django.db.models import Q
        return Chat.objects.filter(
            Q(participant1=self.user) | Q(participant2=self.user),
            id=self.chat_id
        ).exists()
    
    #helps in saving incoming chat messages to the database, associating them with the correct chat room and sender
    @database_sync_to_async
    def save_message(self, message_text):
        chat = Chat.objects.get(id=self.chat_id)
        return Message.objects.create(
            chat=chat,
            sender=self.user,
            message_text=message_text
        )