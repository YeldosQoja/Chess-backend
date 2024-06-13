import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from .models import Game, UserChannel

class MainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        try:
            channel = UserChannel.objects.get(user=self.user)
            channel.name = self.channel_name
            channel.save()
        except ObjectDoesNotExist:
            UserChannel.objects.create(name=self.channel_name, user=self.user)
        finally:
            await self.accept()

    def disconnect(self):
        UserChannel.objects.filter(name=self.channel_name).delete()
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data["type"]
        user_id = data["user_id"]
        dest_channel = UserChannel.objects.filter(user=user_id).first()
        if msg_type == "accept.game":
            game = Game.objects.create(challenger=user_id, opponent=self.user)
            data["game_id"] = game.pk
            await self.channel_layer.send(dest_channel.name, {
                "type": msg_type,
                "data": data,
            })
            await self.channel_layer.send(self.channel_name, {
                "type": data["type"],
                "data": data,
            })
        else:
            await self.channel_layer.send(dest_channel.name, {
                "type": msg_type,
                "data": data,
            })
    
    async def add_friend(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))

    async def accept_friend(self, event):
        data = event["data"]
        friend = data["user_id"]
        self.user.friends.add(friend)
        await self.send(text_data=json.dumps(data))

    async def challenge(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))

    async def start_game(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))
            


# class ChatConsumer(AsyncWebsocketConsumer):
#     pass
    


