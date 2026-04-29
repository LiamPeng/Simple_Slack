from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.workspaces.services import create_workspace_with_creator


User = get_user_model()


class ChannelApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="Pass123456!")
        token = self.client.post(reverse("login"), {"username": "alice", "password": "Pass123456!"}, format="json").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.workspace = create_workspace_with_creator(creator=self.user, name="WS", description="")

    def test_create_channel(self):
        res = self.client.post(
            reverse("workspace-channel-create", kwargs={"workspace_id": self.workspace.id}),
            {"name": "general", "channel_type": "public"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_forbidden_for_non_member(self):
        other = User.objects.create_user(username="bob", password="Pass123456!")
        token = self.client.post(reverse("login"), {"username": "bob", "password": "Pass123456!"}, format="json").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res = self.client.post(
            reverse("workspace-channel-create", kwargs={"workspace_id": self.workspace.id}),
            {"name": "private", "channel_type": "private"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
