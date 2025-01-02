from django.test import TestCase, RequestFactory
from chess.views import user_signin, CreateUserView
from chess.models import User, Friendship, FriendRequest, Game
from chess.serializers import UserSerializer, GameSerializer
from rest_framework.test import APIClient
from django.urls import reverse
from chess.logic.game.chess import Chess
from django.utils import timezone
import json


class AuthViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.api_client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com", username="test", password="12345"
        )

    def test_sign_in_existent_user(self):
        response = self.api_client.post(
            reverse("signin"), {"email": "test@test.com", "password": "12345"}
        )
        self.assertEqual(response.status_code, 201)

    def test_sign_in_non_existent_user(self):
        request = self.factory.post(
            reverse("signin"),
            {"email": "non_existent_user@test.com", "password": "12345"},
        )
        response = user_signin(request)
        self.assertEqual(response.status_code, 404)

    def test_sign_in_with_invalid_data(self):
        request = self.factory.post(
            reverse("signin"), {"username": "test@test.com", "key": "12345"}
        )
        response = user_signin(request)
        self.assertEqual(response.status_code, 400)

    def test_create_user_with_valid_data(self):
        request = self.factory.post(
            reverse("signup"),
            {
                "email": "new.test@test.com",
                "username": "new.test",
                "password": "12345",
                "first_name": "test",
                "last_name": "user",
            },
        )
        response = CreateUserView.as_view()(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email="new.test@test.com").exists())


class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", username="test", password="12345"
        )
        self.friend = User.objects.create_user(
            email="friend@test.com", username="friend", password="12345"
        )
        game1 = Game.objects.create(white=self.user, black=self.friend)
        game2 = Game.objects.create(white=self.friend, black=self.user)
        game3 = Game.objects.create(white=self.user, black=self.friend)
        self.games = [game1, game2, game3]

    def test_user_wins_count(self):
        self.games[0].finish(winner=self.user)
        self.games[1].finish(winner=self.user)
        user_games = self.user.profile.games()
        user_wins = self.user.profile.wins()
        self.assertEqual(user_games.count(), 2)
        self.assertEqual(user_wins, 2)


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", username="test", password="12345"
        )
        self.friend = User.objects.create_user(
            email="friend@test.com", username="friend", password="12345"
        )
        self.game = Game.objects.create(white=self.user, black=self.friend)
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        self.game.finish(winner=self.user)
        serializer = GameSerializer(self.game)
        response = self.api_client.get(reverse("profile-game-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], serializer.data["id"])

    def test_get_user_profile_by_id(self):
        response = self.api_client.get(reverse("user-detail", args=(self.user.pk,)))
        self.assertEqual(response.status_code, 200)


class UserListViewTests(TestCase):
    def setUp(self):
        usernames = ["oscar", "john", "alice", "bob", "william"]
        self.users = []
        for username in usernames:
            user = User.objects.create_user(
                username=username, email=f"{username}@test.com", password="12345"
            )
            self.users.append(user)
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.users[0])

    def test_without_query_params(self):
        response = self.api_client.get(reverse("user-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_with_query_params(self):
        response = self.api_client.get(reverse("user-list"), {"query": "o"})
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(len(data), 2)
        self.assertEqual([user["username"] for user in data], ["john", "bob"])


class FriendshipModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", username="test", password="12345"
        )
        self.friend = User.objects.create_user(
            email="friend@test.com", username="friend", password="12345"
        )
        self.user.friends.add(self.friend)
        self.friend.friends.add(self.user)

    def test_break_friendship_from_user(self):
        friendship = Friendship.objects.get(user=self.user, friend=self.friend)
        friendship.break_friendship()
        self.assertEqual(Friendship.objects.count(), 0)

    def test_break_friendship_from_friend(self):
        friendship = Friendship.objects.get(user=self.friend, friend=self.user)
        friendship.break_friendship()
        self.assertEqual(Friendship.objects.count(), 0)


class FriendRequestModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", username="test", password="12345"
        )
        self.friend = User.objects.create_user(
            email="friend@test.com", username="friend", password="12345"
        )
        self.friend_request = FriendRequest.objects.create(
            sender=self.user, receiver=self.friend
        )

    def test_accept(self):
        self.friend_request.accept()
        user_friends = self.user.friends.all()
        friend_friends = self.friend.friends.all()
        self.assertIn(self.friend, user_friends)
        self.assertIn(self.user, friend_friends)

    def test_accept_after_decline(self):
        self.friend_request.decline()
        self.friend_request.accept()
        user_friends = self.user.friends.all()
        friend_friends = self.friend.friends.all()
        self.assertNotIn(self.friend, user_friends)
        self.assertNotIn(self.user, friend_friends)


class FriendRequestViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", username="test", password="12345"
        )
        self.friend = User.objects.create_user(
            email="friend@test.com", username="friend", password="12345"
        )
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)

    def test_add_friend(self):
        # Request that creates a friend request from self.user to self.friend
        response = self.api_client.post(reverse("friend-add", args=(self.friend.pk,)))
        # Check if request is successful
        self.assertEqual(response.status_code, 201)
        # Get a list of friend's incoming requests
        self.api_client.force_authenticate(user=self.friend)
        response = self.api_client.get(reverse("profile-request-list"))
        data = response.data
        # Check if friend's incoming request list includes the request from self.user
        self.assertEqual(response.status_code, 200)
        serializer = UserSerializer(data=self.user)
        if serializer.is_valid():
            self.assertEqual(data[0]["sender"], serializer.data)

    def test_accept_friend(self):
        friend_request = FriendRequest.objects.create(
            sender=self.friend, receiver=self.user
        )
        # self.user accepts a friend request from self.user
        response = self.api_client.post(
            reverse("friend-accept-request", args=(friend_request.pk,))
        )
        # Check if they include each other in their friend list
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data,
            {"message": f"You and {self.friend} have become friends."},
        )

    def test_decline_friend(self):
        friend_request = FriendRequest.objects.create(
            sender=self.friend, receiver=self.user
        )
        # self.user declines a friend request from self.user
        response = self.api_client.post(
            reverse("friend-decline-request", args=(friend_request.pk,))
        )
        # Check if they include each other in their friend list
        self.assertEqual(response.status_code, 200)

    def test_remove_friend(self):
        self.user.friends.add(self.friend)
        self.friend.friends.add(self.user)
        # self.user breaks a friendship with self.friend
        response = self.api_client.delete(
            reverse("friend-remove", args=(self.friend.pk,))
        )
        # Check if they are no longer friends
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user, self.friend.friends.all())
        self.assertNotIn(self.friend, self.user.friends.all())


class MakeMoveViewTests(TestCase):
    def setUp(self):
        self.white = User.objects.create_user(
            email="test@test.com", username="test", password="12345"
        )
        self.black = User.objects.create_user(
            email="friend@test.com", username="friend", password="12345"
        )
        self.game = Game.objects.create(white=self.white, black=self.black)
        self.white_api_client = APIClient()
        self.white_api_client.force_authenticate(user=self.white)
        self.black_api_client = APIClient()
        self.black_api_client.force_authenticate(user=self.black)

    def test_first_move(self):
        response = self.white_api_client.post(
            reverse("game-move", args=(self.game.pk,)),
            json.dumps(
                {
                    "start_square": [6, 3],
                    "end_square": [4, 3],
                    "timestamp": str(timezone.now()),
                }
            ),
            content_type="application/json",
        )
        self.game.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.game.moves.count(), 1)
        self.assertEqual(self.game.fen_notation, "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3")

    def test_inactive_color_move(self):
        response = self.white_api_client.post(
            reverse("game-move", args=(self.game.pk,)),
            json.dumps(
                {
                    "start_square": [1, 3],
                    "end_square": [3, 3],
                    "timestamp": str(timezone.now()),
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "The move is invalid")

    def test_invalid_move(self):
        # e4
        response = self.white_api_client.post(
            reverse("game-move", args=(self.game.pk,)),
            json.dumps(
                {
                    "start_square": [6, 4],
                    "end_square": [4, 4],
                    "timestamp": str(timezone.now()),
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        # Nh6
        response = self.black_api_client.post(
            reverse("game-move", args=(self.game.pk,)),
            json.dumps(
                {
                    "start_square": [0, 6],
                    "end_square": [2, 7],
                    "timestamp": str(timezone.now()),
                }
            ),
            content_type="application/json",
        )
        self.game.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.game.fen_notation, "rnbqkb1r/pppppppp/7n/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -")

        # invalid move - Bh3
        response = self.white_api_client.post(
            reverse("game-move", args=(self.game.pk,)),
            json.dumps(
                {
                    "start_square": [7, 5],
                    "end_square": [5, 7],
                    "timestamp": str(timezone.now()),
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "The move is invalid")

    
