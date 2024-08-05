from django.urls import re_path
from .consumers import MainConsumer, GameConsumer

websocket_urlpatterns = [
    re_path(r"^ws/main", MainConsumer.as_asgi(), name="main"),
    re_path(r"^ws/games/(?P<room_name>\w+-\d+)/$", GameConsumer.as_asgi(), name="game"),
]