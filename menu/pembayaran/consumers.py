import json
from channels.generic.websocket import AsyncWebsocketConsumer
from config import midtrans
MIDTRANS_CORE = midtrans.MIDTRANS_CORE
PAYMENT_STATUS = midtrans.PAYMENT_STATUS
class TransaksiConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.id_transaksi = self.scope["url_route"]["kwargs"]["id_transaksi"]
        await self.channel_layer.group_add(
            self.id_transaksi,
            self.channel_name
        )
        resp = MIDTRANS_CORE.transactions.status(self.id_transaksi)
        await self.channel_layer.group_send(
            self.id_transaksi,
            {
                'type': 'status_transaksi',
                "resp": PAYMENT_STATUS[resp['transaction_status']]
            }
        )

      
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.id_transaksi,
            self.channel_name
        )

    async def status_transaksi(self, event):
        resp = event['resp']
        await self.send(text_data=json.dumps(resp))

 