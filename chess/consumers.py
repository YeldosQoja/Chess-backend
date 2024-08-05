import json
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from channels.db import database_sync_to_async
from .models import UserChannel


class MainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        try:
            channel = await database_sync_to_async(UserChannel.objects.get)(
                user=self.user.pk
            )
            channel.name = self.channel_name
            await database_sync_to_async(channel.save)()
        except ObjectDoesNotExist:
            await database_sync_to_async(UserChannel.objects.create)(
                name=self.channel_name, user=self.user
            )
        finally:
            await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        print(text_data)

    async def disconnect(self, code):
        await self.delete_channel()
        await self.close()

    async def on_challenge(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "challenge",
                    "request_id": event["request_id"],
                    "user": {
                        "id": self.user.pk,
                        "username": self.user.username,
                        "name": self.user.first_name + self.user.last_name,
                    },
                }
            )
        )

    async def on_challenge_accept(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "challenge_accepted",
                    "game_id": event["game_id"],
                }
            )
        )

    async def on_movement(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "move",
                    "game_id": event["game_id"],
                    "from": event["from"],
                    "to": event["to"],
                }
            )
        )

    @database_sync_to_async
    def delete_channel(self):
        UserChannel.objects.filter(name=self.channel_name).delete()