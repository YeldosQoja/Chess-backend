from django.urls import path
from .views import *

urlpatterns = [
    path("home/", home, name="home"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/friends/", ProfileFriendListView.as_view(), name="profile-friend-list"),
    path("profile/games/", ProfileGameListView.as_view(), name="profile-game-list"),
    path("profile/requests/", FriendRequestListView.as_view(), name="profile-request-list"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/friends/", FriendListView.as_view(), name="user-friend-list"),
    path("users/<int:pk>/games/", user_games, name="user-game-list"),
    path("friends/<int:pk>/add/", add_friend, name="friend-add"),
    path("friends/<int:pk>/remove/", remove_friend, name="friend-remove"),
    path("friends/requests/<int:pk>/accept/", accept_friend, name="friend-accept-request"),
    path("friends/requests/<int:pk>/decline/", decline_friend, name="friend-decline-request"),
    path("games/<int:pk>/", GameRetrieveView.as_view(), name="game-detail"),
    path("games/<int:pk>/finish/", finish_game, name="game-finish"),
    path("games/challenges/send/<str:username>/", send_challenge, name="game-challenge-send"),
    path("games/challenges/<int:pk>/accept/", accept_challenge, name="game-challenge-accept"),
    path("games/challenges/<int:pk>/decline/", decline_challenge, name="game-challenge-decline"),
    path("games/<int:pk>/move/make/", make_move, name="game-move"),
    path("games/<int:pk>/move/validate/", validate_move, name="game-move-validate"),
    path("games/<int:pk>/valid_moves/<str:square>/", get_valid_moves, name="game-valid-moves"),
]
