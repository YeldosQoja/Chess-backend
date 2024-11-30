import json
from channels.generic.websocket import (
    AsyncWebsocketConsumer,
    AsyncJsonWebsocketConsumer,
)

class MainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if self.user.is_anonymous:
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
                    "request_id": event["request_id"],
                    "username": self.username,
                }
            )
        )

    async def challenge_accept(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "challenge_accept",
                    "game_id": event["game_id"],
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
                "timestamp": move["timestamp"],
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
                "timestamp": promotion["timestamp"],
            },
        )

    async def send_resign(self, data):
        pass

    async def chess_move(self, event):
        await self.send_json(
            {
                "msg_type": "move",
                "player": event["player"],
                "from": event["from"],
                "to": event["to"],
                "timestamp": event["timestamp"],
            }
        )

    async def chess_promote(self, event):
        await self.send_json(
            {
                "msg_type": "promote",
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