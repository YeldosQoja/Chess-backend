from django.test import TestCase, RequestFactory
from .views import user_signin, CreateUserView, ProfileUserRetrieveView
from .models import User


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
    

