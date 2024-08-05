import json
from channels.generic.websocket import (
    AsyncWebsocketConsumer,
    AsyncJsonWebsocketConsumer,
)
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
        except UserChannel.DoesNotExist:
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


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()

    async def receive_json(self, content, **kwargs):
        command = content.get("command", None)
        if command == "move":
            await self.send_move(content)
        elif command == "promote":
            await self.send_promotion(content)
        elif command == "resign":
            await self.send_resign(content)
        
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def send_move(self, move):
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chess.move",
                "player": move["player"],
                "from": move["from"],
                "to": move["to"],
            },
        )
    
    async def send_promotion(self, promotion):
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chess.promote",
                "player": promotion["player"],
                "square": promotion["square"],
                "piece": promotion["piece"],
            }
        )

    async def send_resign(self, data):
        pass

    async def chess_move(self, event):
        await self.send_json({
            "msg_type": "move",
            "player": event["player"],
            "from": event["from"],
            "to": event["to"],
        })

    async def chess_promote(self, event):
        await self.send_json({
            "msg_type": "promote",
            "player": event["player"],
            "square": event["square"],
            "piece": event["piece"],
        })

    async def chess_resign(self, event):
        pass

    async def chess_win(self, event):
        pass
