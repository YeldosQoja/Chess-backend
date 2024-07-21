from django.urls import path
from .views import (
    FriendListView,
    FriendRequestListView,
    add_friend,
    accept_friend,
    decline_friend,
    remove_friend,
    send_challenge,
    accept_challenge,
)

urlpatterns = [
    path("friends/", FriendListView.as_view(), name="friend-list"),
    path("friends/requests/", FriendRequestListView.as_view(), name="friend-request-list"),
    path("friends/add/", add_friend, name="friend-add"),
    path("friends/accept/", accept_friend, name="friend-accept"),
    path("friends/decline/", decline_friend, name="friend-decline"),
    path("friends/remove/", remove_friend, name="friend-remove"),
    path("game/challenge/send", send_challenge, name="challenge-send"),
    path("game/challenge/accept", accept_challenge, name="challenge-accept"),
]
