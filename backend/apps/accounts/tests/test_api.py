from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthApiTests(APITestCase):
    def test_register_and_me(self):
        res = self.client.post(
            reverse("register"),
            {"username": "alice", "email": "a@example.com", "password": "VeryStrongPass123!"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", res.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        me_res = self.client.get(reverse("me"))
        self.assertEqual(me_res.status_code, status.HTTP_200_OK)
        self.assertEqual(me_res.data["username"], "alice")

    def test_login_invalid_credentials(self):
        User.objects.create_user(username="bob", email="b@example.com", password="Pass123456!")
        res = self.client.post(reverse("login"), {"username": "bob", "password": "wrong"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
