import json
from channels.generic.websocket import (
    AsyncWebsocketConsumer,
    AsyncJsonWebsocketConsumer,
)

class MainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
        else:
            self.username = user.username
            await self.channel_layer.group_add(self.username, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.username, self.channel_name)
        await self.close()

    async def game_challenge(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "challenge",
                    "requestId": event["request_id"],
                    "username": event["username"],
                }
            )
        )

    async def challenge_accept(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "challenge_accept",
                    "gameId": event["game_id"],
                }
            )
        )


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        type = content.get("type", None)
        if type:
            content["type"] = f"chess.{type}"
            await self.channel_layer.group_send(self.room_name, content)

    async def chess_move(self, event):
        await self.send_json(
            {
                "type": "move",
                "player": event["player"],
                "from": event["from"],
                "to": event["to"],
                "timestamp": event["timestamp"],
            }
        )

    async def chess_promotion(self, event):
        await self.send_json(
            {
                "type": "promotion",
                "player": event["player"],
                "square": event["square"],
                "piece": event["piece"],
                "timestamp": event["timestamp"],
            }
        )

    async def chess_resign(self, event):
        pass

    async def chess_win(self, event):
        pass
