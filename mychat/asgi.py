import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mychat.settings")

django_asgi_app = get_asgi_application()

# BOTH websocket route groups
from base.routing import websocket_urlpatterns as chat_routes
from base.routing_room import websocket_urlpatterns as room_routes

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                chat_routes + room_routes
            )
        )
    ),
})