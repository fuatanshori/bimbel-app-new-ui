from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(
        'ws/chat/<group_id>/', consumers.ChatConsumers.as_asgi(),
	),
]