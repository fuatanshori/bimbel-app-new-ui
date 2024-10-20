import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from menu.pembayaran.models import Transaksi
from .models import Chat, Modul
from menu.utils.encode_url import decode_id
from django.utils import timezone


class ChatConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        self.id = self.scope["url_route"]["kwargs"]["group_id"]
        self.group_id = decode_id(self.id)
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            valid_user = await self.get_valid_user(user=self.user)
            if valid_user:
                await self.channel_layer.group_add(
                    self.group_id,
                    self.channel_name
                )
                await self.accept()
            else:
                await self.close()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_id,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        chat_obj = await self.add_chat(message)
        await self.channel_layer.group_send(
            self.group_id,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': str(self.user.pk),
                'full_name': self.user.full_name,
                'timestamp': timezone.localtime(chat_obj.timestamp).strftime("%B %d, %Y %H:%M")
            }
        )

    async def chat_message(self, event):
        is_user = event['user_id'] == str(self.user.pk)
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'is_user': is_user,
            'full_name': event['full_name'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def get_valid_user(self, user):
        try:
            Transaksi.objects.get(user=user, transaksi_status="settlement")
            return True
        except Transaksi.DoesNotExist:
            return user.role in ["admin", "pemateri"]

    @database_sync_to_async
    def add_chat(self, message):
        modul_obj = Modul.objects.get(pk=self.group_id)
        chat = Chat.objects.create(user=self.user, modul=modul_obj, message=message, timestamp=timezone.now())
        chat.save()
        return chat