from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.channels.services import create_channel_with_creator
from backend.apps.messages.models import Message
from backend.apps.workspaces.services import create_workspace_with_creator


User = get_user_model()


class MessageApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", email="alice@example.com", password="Pass123456!")
        token = self.client.post(reverse("login"), {"username": "alice", "password": "Pass123456!"}, format="json").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        workspace = create_workspace_with_creator(creator=self.user, name="WS", description="")
        self.channel = create_channel_with_creator(workspace=workspace, creator=self.user, name="general", channel_type="public")

    def test_create_and_search_message(self):
        create_res = self.client.post(
            reverse("channel-messages", kwargs={"channel_id": self.channel.id}),
            {"body": "hello world"},
            format="json",
        )
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Message.objects.filter(channel=self.channel).exists())

        search_res = self.client.get(reverse("message-search") + "?q=hello")
        self.assertEqual(search_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(search_res.data), 1)
