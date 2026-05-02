from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.workspaces.services import create_workspace_with_creator
from backend.apps.workspaces.models import WorkspaceMembership

from ..models import Channel
from ..services import create_channel_with_creator, create_direct_channel


User = get_user_model()


class ChannelApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", email="alice@example.com", password="Pass123456!")
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

    def test_generic_create_rejects_direct_channel(self):
        res = self.client.post(
            reverse("workspace-channel-create", kwargs={"workspace_id": self.workspace.id}),
            {"name": "dm-alice-bob", "channel_type": "direct"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_forbidden_for_non_member(self):
        other = User.objects.create_user(username="bob", email="bob@example.com", password="Pass123456!")
        token = self.client.post(reverse("login"), {"username": "bob", "password": "Pass123456!"}, format="json").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res = self.client.post(
            reverse("workspace-channel-create", kwargs={"workspace_id": self.workspace.id}),
            {"name": "private", "channel_type": "private"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_service_rejects_direct_channel_from_generic_create(self):
        with self.assertRaises(ValueError):
            create_channel_with_creator(
                workspace=self.workspace,
                creator=self.user,
                name="dm-invalid",
                channel_type=Channel.ChannelType.DIRECT,
            )

    def test_service_rejects_channel_for_non_workspace_member(self):
        other = User.objects.create_user(username="charlie", email="charlie@example.com", password="Pass123456!")
        with self.assertRaises(PermissionError):
            create_channel_with_creator(
                workspace=self.workspace,
                creator=other,
                name="private",
                channel_type=Channel.ChannelType.PRIVATE,
            )

    def test_create_direct_channel_requires_workspace_members(self):
        other = User.objects.create_user(username="dana", email="dana@example.com", password="Pass123456!")
        with self.assertRaises(ValueError):
            create_direct_channel(workspace=self.workspace, creator=self.user, other_user=other)

    def test_create_direct_channel_adds_exactly_two_members(self):
        other = User.objects.create_user(username="erin", email="erin@example.com", password="Pass123456!")
        WorkspaceMembership.objects.create(workspace=self.workspace, user=other)

        channel = create_direct_channel(workspace=self.workspace, creator=self.user, other_user=other)

        self.assertEqual(channel.channel_type, Channel.ChannelType.DIRECT)
        self.assertEqual(channel.memberships.count(), 2)

    def test_direct_channel_create_endpoint(self):
        other = User.objects.create_user(username="frank", email="frank@example.com", password="Pass123456!")
        WorkspaceMembership.objects.create(workspace=self.workspace, user=other)

        res = self.client.post(
            reverse("workspace-direct-channel-create", kwargs={"workspace_id": self.workspace.id}),
            {"other_user_id": other.id},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["channel_type"], Channel.ChannelType.DIRECT)
        self.assertEqual(res.data["other_user"]["id"], other.id)

    def test_direct_channel_create_endpoint_rejects_non_workspace_member(self):
        other = User.objects.create_user(username="grace", email="grace@example.com", password="Pass123456!")

        res = self.client.post(
            reverse("workspace-direct-channel-create", kwargs={"workspace_id": self.workspace.id}),
            {"other_user_id": other.id},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_direct_channel_get_or_create_endpoint_reuses_existing_channel(self):
        other = User.objects.create_user(username="hannah", email="hannah@example.com", password="Pass123456!")
        WorkspaceMembership.objects.create(workspace=self.workspace, user=other)

        first = self.client.post(
            reverse("workspace-direct-channel-get-or-create", kwargs={"workspace_id": self.workspace.id}),
            {"other_user_id": other.id},
            format="json",
        )
        second = self.client.post(
            reverse("workspace-direct-channel-get-or-create", kwargs={"workspace_id": self.workspace.id}),
            {"other_user_id": other.id},
            format="json",
        )

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertEqual(Channel.objects.filter(channel_type=Channel.ChannelType.DIRECT).count(), 1)
