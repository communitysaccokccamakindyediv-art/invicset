from django.urls import re_path
from .consumers_room import RoomChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/room/chat/(?P<room_name>[^/]+)/$", RoomChatConsumer.as_asgi()),
]