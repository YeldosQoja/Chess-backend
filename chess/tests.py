from django.test import TestCase, RequestFactory
from .views import user_signin, CreateUserView
from .models import User, Friendship, FriendRequest
from rest_framework.test import APIClient
from django.urls import reverse

class AuthViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email="test@test.com", username="test", password="12345"
        )

    def test_sign_in_existent_user(self):
        request = self.factory.post(
            "api/signin/", {"email": "test@test.com", "password": "12345"}
        )
        response = user_signin(request)
        self.assertEqual(response.status_code, 201)

    def test_sign_in_non_existent_user(self):
        request = self.factory.post(
            "api/signin/", {"email": "non_existent_user@test.com", "password": "12345"}
        )
        response = user_signin(request)
        self.assertEqual(response.status_code, 404)

    def test_sign_in_with_invalid_data(self):
        request = self.factory.post(
            "api/signin/", {"username": "test@test.com", "key": "12345"}
        )
        response = user_signin(request)
        self.assertEqual(response.status_code, 400)

    def test_create_user_with_valid_data(self):
        request = self.factory.post(
            "api/signup/",
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


class FriendSystemAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", username="test", password="12345"
        )
        self.friend = User.objects.create_user(
            email="friend@test.com", username="friend", password="12345"
        )
        self.api_client = APIClient()

    def test_add_friend(self):
        # Request that creates a friend request from self.user to self.friend
        self.api_client.force_authenticate(user=self.user)
        response = self.api_client.post(reverse("friend-add"), {"friend": self.friend.pk})
        # Check if request is successful
        self.assertEqual(response.status_code, 201)
        # Get a list of friend's incoming requests
        self.api_client.force_authenticate(user=self.friend)
        response = self.api_client.get(reverse("friend-request-list"))
        # Check if friend's incoming request list includes the request from self.user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.pk, response.data[0]["sender"])
    
    def test_accept_friend(self):
        # Request that creates a friend request from self.user to self.friend
        self.api_client.force_authenticate(user=self.user)
        self.api_client.post(reverse("friend-add"), {"friend": self.friend.pk})
        # self.friend accepts a friend request from self.user
        self.api_client.force_authenticate(user=self.friend)
        response = self.api_client.post(reverse("friend-accept"), {"friend": self.user.pk})
        # Check if they include each other in their friend list
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, { "message": f"You and {self.user.username} have become friends." })
    
    def test_decline_friend(self):
        # Request that creates a friend request from self.user to self.friend
        self.api_client.force_authenticate(user=self.user)
        self.api_client.post(reverse("friend-add"), {"friend": self.friend.pk})
        # self.friend declines a friend request from self.user
        self.api_client.force_authenticate(user=self.friend)
        response = self.api_client.post(reverse("friend-decline"), {"friend": self.user.pk})
        # Check if they include each other in their friend list
        self.assertEqual(response.status_code, 200)
    
    def test_remove_friend(self):
        self.user.friends.add(self.friend)
        self.friend.friends.add(self.user)
        # self.user breaks a friendship with self.friend
        self.api_client.force_authenticate(user=self.user)
        response = self.api_client.delete(reverse("friend-remove"), {"friend": self.friend.pk})
        # Check if they are no longer friends
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user, self.friend.friends.all())
        self.assertNotIn(self.friend, self.user.friends.all())
