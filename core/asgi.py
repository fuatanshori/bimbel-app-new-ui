import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from menu.pembayaran.routing import websocket_urlpatterns as pembayaran_live_websocket_urlpatterns
from menu.modul.routing import websocket_urlpatterns as modul_chat_websocket_urlpattern

django_asgi_app = get_asgi_application()
url_ws = pembayaran_live_websocket_urlpatterns+modul_chat_websocket_urlpattern
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(url_ws))
        ),
    }
)
