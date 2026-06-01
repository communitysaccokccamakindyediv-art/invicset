# consumers.py

import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import (
    ChatMessage,
    ChatRoom,
    RoomParticipant,
)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        self.room_group_name = f"chat_{self.room_name}"

        self.user = self.scope["user"]

        # Join room channel
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Create/get room
        self.room = await self.get_or_create_room(self.room_name)

        # Add participant
        await self.add_participant()

        # System join message
        await self.create_system_message(
            f"{self.user.username} joined the room"
        )

        # Notify room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "system_message",
                "message": f"{self.user.username} joined the room"
            }
        )

        # Send updated participant list
        await self.send_participants()

    async def disconnect(self, close_code):

        # Mark offline
        await self.mark_offline()

        # Notify room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "system_message",
                "message": f"{self.user.username} left the room"
            }
        )

        # Save system message
        await self.create_system_message(
            f"{self.user.username} left the room"
        )

        # Leave channel
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Update participants
        await self.send_participants()

    async def receive(self, text_data):
        data = json.loads(text_data)

        event_type = data.get("type")

        # CHAT MESSAGE
        if event_type == "chat":

            message = data.get("message")

            # Save message
            await self.save_message(message)

            # Broadcast
            saved_message = await self.save_message(message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": self.user.username,
                    "message_id": saved_message.id,
                }
            )

        elif event_type == "file_shared":

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "room_file_shared",
                    "file_name": data["file_name"],
                    "file_url": data["file_url"],
                    "uploaded_by": self.user.username,
                }
            )

        # TYPING
        elif event_type == "typing":

            is_typing = data.get("is_typing", False)

            await self.update_typing_status(is_typing)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_status",
                    "username": self.user.username,
                    "is_typing": is_typing
                }
            )

        # REMOVE USER

        elif event_type == "remove_user":

            username = data.get("username")

            # Only host can remove
            if await self.is_host():

                await self.remove_participant(username)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "user_removed",
                        "username": username,
                        "removed_by": self.user.username,
                    }
                )

                await self.send_participants()

    async def room_file_shared(self, event):

        await self.send(text_data=json.dumps({
            "type": "file_shared",
            "file_name": event["file_name"],
            "file_url": event["file_url"],
            "uploaded_by": event["uploaded_by"],
        }))
         
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"],
            "username": event["username"],
            "message_id": event["message_id"]
        }))

    async def system_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "system",
            "message": event["message"]
        }))

    async def typing_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "username": event["username"],
            "is_typing": event["is_typing"]
        }))

    async def participants_list(self, event):
        await self.send(text_data=json.dumps({
            "type": "participants",
            "participants": event["participants"]
        }))

    async def user_removed(self, event):

        await self.send(text_data=json.dumps({
            "type": "removed",
            "username": event["username"],
            "removed_by": event["removed_by"]
        }))

    # DATABASE METHODS

    @database_sync_to_async
    def get_or_create_room(self, room_name):

        room, created = ChatRoom.objects.get_or_create(
            name=room_name
        )

        # First user becomes host
        if created:
            room.host = self.user
            room.save()

        return room

    @database_sync_to_async
    def add_participant(self):

        role = "participant"

        if self.room.host == self.user:
            role = "host"

        participant, created = RoomParticipant.objects.get_or_create(
            room=self.room,
            user=self.user,
            defaults={
                "role": role,
                "is_online": True
            }
        )

        participant.is_online = True
        participant.save()

        return participant

    @database_sync_to_async
    def mark_offline(self):

        try:
            participant = RoomParticipant.objects.get(
                room=self.room,
                user=self.user
            )

            participant.is_online = False
            participant.is_typing = False
            participant.save()

        except RoomParticipant.DoesNotExist:
            pass

    @database_sync_to_async
    def save_message(self, message):

        return ChatMessage.objects.create(
            room=self.room,
            sender=self.user,
            message=message,
            message_type='user'
        )

    @database_sync_to_async
    def create_system_message(self, message):

        return ChatMessage.objects.create(
            room=self.room,
            sender=None,
            message=message,
            message_type='system'
        )

    @database_sync_to_async
    def update_typing_status(self, is_typing):

        try:
            participant = RoomParticipant.objects.get(
                room=self.room,
                user=self.user
            )

            participant.is_typing = is_typing
            participant.save()

        except RoomParticipant.DoesNotExist:
            pass

    @database_sync_to_async
    def get_participants(self):

        participants = RoomParticipant.objects.filter(
            room=self.room,
            is_online=True
        ).select_related('user')

        return [
            {
                "username": p.user.username,
                "profile_picture": (
                    p.user.profile_picture.url
                    if p.user.profile_picture
                    else ""
                ),
                "role": p.role,
            }
            for p in participants
        ]

    async def send_participants(self):

        participants = await self.get_participants()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "participants_list",
                "participants": participants
            }
        )
    @database_sync_to_async
    def is_host(self):

        return self.room.host == self.user


    @database_sync_to_async
    def remove_participant(self, username):

        try:

            participant = RoomParticipant.objects.get(
                room=self.room,
                user__username=username
            )

            participant.delete()

        except RoomParticipant.DoesNotExist:
            pass