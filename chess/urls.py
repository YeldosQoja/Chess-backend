from django.urls import path
from .views import (
    UserListView,
    UserDetailView,
    ProfileView,
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
    path("profile/", ProfileView.as_view(), name="profile"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>", UserDetailView.as_view(), name="user-detail"),
    path("friends/", FriendListView.as_view(), name="friend-list"),
    path("friends/requests/", FriendRequestListView.as_view(), name="friend-request-list"),
    path("friends/add/", add_friend, name="friend-add"),
    path("friends/accept/", accept_friend, name="friend-accept"),
    path("friends/decline/", decline_friend, name="friend-decline"),
    path("friends/remove/", remove_friend, name="friend-remove"),
    path("game/challenge/send", send_challenge, name="challenge-send"),
    path("game/challenge/accept", accept_challenge, name="challenge-accept"),
]
