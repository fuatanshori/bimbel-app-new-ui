from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(
        'ws/pembayaran/<id_transaksi>/', consumers.TransaksiConsumer.as_asgi(),
	),
]