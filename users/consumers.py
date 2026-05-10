import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message


class ChatConsumer(AsyncWebsocketConsumer):
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

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get('type')

        if msg_type == 'chat_message':
            message_text = data.get('message_text', '').strip()
            if not message_text:
                return
            message = await self.save_message(message_text)
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'chat_message',
                'id': message.id,
                'message_text': message.message_text,
                'sender_username': self.user.username,
                'is_read': False,
                'created_at': message.created_at.isoformat(),
                'is_system': False,
            })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def is_participant(self):
        from django.db.models import Q
        return Chat.objects.filter(
            Q(participant1=self.user) | Q(participant2=self.user),
            id=self.chat_id
        ).exists()

    @database_sync_to_async
    def save_message(self, message_text):
        chat = Chat.objects.get(id=self.chat_id)
        return Message.objects.create(
            chat=chat,
            sender=self.user,
            message_text=message_text,
            is_system=False,
        )


class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'call_{self.chat_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return
        if not await self.is_participant():
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get('type')
        allowed  = {'call_request', 'call_offer', 'call_answer', 'ice_candidate', 'call_end', 'call_reject'}

        if msg_type not in allowed:
            return

        # always relay the signal so the other peer's UI responds
        await self.channel_layer.group_send(
            self.room_group_name,
            {**data, 'sender_username': self.user.username}
        )

        # save a persistent system message and push to chat group
        if msg_type == 'call_end':
            duration  = data.get('duration', 0)
            call_type = data.get('call_type', 'video')
            mins = duration // 60
            secs = duration % 60
            text = f" {call_type.capitalize()} call ended · {mins:02d}:{secs:02d}"
            message = await self.save_system_message(text)
            await self.channel_layer.group_send(
                f'chat_{self.chat_id}',
                {
                    'type': 'chat_message',
                    'id': message.id,
                    'message_text': message.message_text,
                    'sender_username': self.user.username,
                    'is_read': False,
                    'created_at': message.created_at.isoformat(),
                    'is_system': True,
                }
            )

        elif msg_type == 'call_reject':
            call_type = data.get('call_type', 'video')
            text = f" {call_type.capitalize()} call declined"
            message = await self.save_system_message(text)
            await self.channel_layer.group_send(
                f'chat_{self.chat_id}',
                {
                    'type': 'chat_message',
                    'id': message.id,
                    'message_text': message.message_text,
                    'sender_username': self.user.username,
                    'is_read': False,
                    'created_at': message.created_at.isoformat(),
                    'is_system': True,
                }
            )

    # handler methods — Channels dispatches group messages by matching event type to method name
    async def call_request(self, event):   await self.send(text_data=json.dumps(event))
    async def call_offer(self, event):     await self.send(text_data=json.dumps(event))
    async def call_answer(self, event):    await self.send(text_data=json.dumps(event))
    async def ice_candidate(self, event):  await self.send(text_data=json.dumps(event))
    async def call_end(self, event):       await self.send(text_data=json.dumps(event))
    async def call_reject(self, event):    await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def is_participant(self):
        from django.db.models import Q
        return Chat.objects.filter(
            Q(participant1=self.user) | Q(participant2=self.user),
            id=self.chat_id
        ).exists()

    @database_sync_to_async
    def save_system_message(self, text):
        chat = Chat.objects.get(id=self.chat_id)
        return Message.objects.create(
            chat=chat,
            sender=self.user,
            message_text=text,
            is_system=True,
        )