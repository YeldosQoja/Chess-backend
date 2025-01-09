import json
from channels.generic.websocket import (
    AsyncWebsocketConsumer,
    AsyncJsonWebsocketConsumer,
)
from channels.db import database_sync_to_async
from .models import Game


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
            game = await self.get_game()
            self.color = await database_sync_to_async(game.get_color)(
                self.scope["user"]
            )
            await self.accept()

    @database_sync_to_async
    def get_game(self):
        room_name = self.scope["url_route"]["kwargs"]["room_name"]
        _, game_id = room_name.split("-")
        return Game.objects.get(pk=game_id)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def chess_move(self, event):
        if self.color != event["player"]:
            await self.send_json(
                {
                    "type": "move",
                    "player": event["player"],
                    "from": event["from"],
                    "to": event["to"],
                    "promotion": event["promotion"],
                }
            )

    async def chess_resign(self, event):
        pass
