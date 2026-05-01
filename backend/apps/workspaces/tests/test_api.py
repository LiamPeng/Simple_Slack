from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.workspaces.models import WorkspaceMembership


User = get_user_model()


class WorkspaceApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", email="alice@example.com", password="Pass123456!")
        self.bob = User.objects.create_user(username="bob", email="bob@example.com", password="Pass123456!")
        token = self.client.post(reverse("login"), {"username": "alice", "password": "Pass123456!"}, format="json").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_workspace_creates_admin_membership(self):
        res = self.client.post(reverse("workspace-list-create"), {"name": "WS", "description": "desc"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WorkspaceMembership.objects.filter(workspace_id=res.data["id"], user=self.user, role="admin").exists())

    def test_admin_can_promote_and_remove_member(self):
        workspace = self.client.post(reverse("workspace-list-create"), {"name": "WS"}, format="json").data
        WorkspaceMembership.objects.create(workspace_id=workspace["id"], user=self.bob, role="member")

        promote_res = self.client.patch(
            reverse("workspace-member-role", kwargs={"workspace_id": workspace["id"], "user_id": self.bob.id}),
            {"role": "admin"},
            format="json",
        )
        self.assertEqual(promote_res.status_code, status.HTTP_200_OK)
        self.assertEqual(promote_res.data["role"], "admin")

        remove_res = self.client.delete(
            reverse("workspace-member-delete", kwargs={"workspace_id": workspace["id"], "user_id": self.bob.id})
        )
        self.assertEqual(remove_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(WorkspaceMembership.objects.filter(workspace_id=workspace["id"], user=self.bob).exists())
