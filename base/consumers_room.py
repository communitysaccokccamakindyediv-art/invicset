# consumers_room.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class RoomChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"].get("room_name")

        # IMPORTANT: prevents ws/chat//
        if not self.room_name:
            await self.close()
            return

        self.room_group_name = f"room_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type")

        user = self.scope["user"]
        username = user.username if user.is_authenticated else "Anonymous"

        # CHAT
        if msg_type == "chat":
            message = data.get("message")

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "room_chat_message",
                    "message": message,
                    "username": username,
                }
            )

        # TYPING
        elif msg_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "room_typing",
                    "username": username,
                    "is_typing": data.get("is_typing", False),
                }
            )

    async def room_chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"],
            "username": event["username"],
        }))

    async def room_typing(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "username": event["username"],
            "is_typing": event["is_typing"],
        }))