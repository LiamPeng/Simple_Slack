from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.channels.models import ChannelMembership
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

    def test_mark_channel_read_sets_last_read_at(self):
        Message.objects.create(channel=self.channel, sender=self.user, body="hello")
        read_res = self.client.post(reverse("channel-mark-read", kwargs={"channel_id": self.channel.id}))
        self.assertEqual(read_res.status_code, status.HTTP_204_NO_CONTENT)

        membership = ChannelMembership.objects.get(channel=self.channel, user=self.user)
        self.assertIsNotNone(membership.last_read_at)

    def test_workspace_detail_includes_unread_count_excluding_own_messages(self):
        membership = ChannelMembership.objects.get(channel=self.channel, user=self.user)
        membership.last_read_at = timezone.now()
        membership.save(update_fields=["last_read_at"])

        other = User.objects.create_user(username="bob", email="bob@example.com", password="Pass123456!")
        workspace = self.channel.workspace
        ChannelMembership.objects.create(channel=self.channel, user=other)
        workspace.memberships.create(user=other, role="member")

        Message.objects.create(channel=self.channel, sender=other, body="from bob")
        Message.objects.create(channel=self.channel, sender=self.user, body="from alice")

        workspace_res = self.client.get(reverse("workspace-detail", kwargs={"workspace_id": workspace.id}))
        self.assertEqual(workspace_res.status_code, status.HTTP_200_OK)
        channel_data = next(c for c in workspace_res.data["channels"] if c["id"] == self.channel.id)
        self.assertEqual(channel_data["unread_count"], 1)
