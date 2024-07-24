from django.urls import path
from .views import (
    UserListView,
    UserDetailView,
    ProfileView,
    ProfileFriendListView,
    ProfileGameListView,
    FriendListView,
    FriendRequestListView,
    add_friend,
    accept_friend,
    decline_friend,
    remove_friend,
    send_challenge,
    accept_challenge,
    GameListView,
)

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/friends/", ProfileFriendListView.as_view(), name="profile-friend-list"),
    path("profile/games/", ProfileGameListView.as_view(), name="profile-game-list"),
    path("profile/requests/", FriendRequestListView.as_view(), name="profile-request-list"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/friends/", FriendListView.as_view(), name="friend-list"),
    path("users/<int:pk>/games/", GameListView.as_view(), name="game-list"),
    path("friends/<int:pk>/add/", add_friend, name="friend-add"),
    path("friends/<int:pk>/remove/", remove_friend, name="friend-remove"),
    path("friends/requests/<int:pk>/accept/", accept_friend, name="friend-accept-request"),
    path("friends/requests/<int:pk>/decline/", decline_friend, name="friend-decline-request"),
    path("games/<int:pk>/", GameListView.as_view(), name="game-list"),
    path("games/challenge/send/<int:user_id>/", send_challenge, name="challenge-send"),
    path("games/challenge/accept/<int:pk>/", accept_challenge, name="challenge-accept"),
]
