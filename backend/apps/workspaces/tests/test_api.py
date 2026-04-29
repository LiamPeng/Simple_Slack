from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.workspaces.models import WorkspaceMembership


User = get_user_model()


class WorkspaceApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="Pass123456!")
        token = self.client.post(reverse("login"), {"username": "alice", "password": "Pass123456!"}, format="json").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_workspace_creates_admin_membership(self):
        res = self.client.post(reverse("workspace-list-create"), {"name": "WS", "description": "desc"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WorkspaceMembership.objects.filter(workspace_id=res.data["id"], user=self.user, role="admin").exists())
