from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.invitations.models import Invitation
from backend.apps.workspaces.models import Workspace, WorkspaceMembership
from backend.apps.workspaces.services import create_workspace_with_creator


User = get_user_model()


class WorkspaceApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", email="alice@example.com", password="Pass123456!")
        self.bob = User.objects.create_user(username="bob", email="bob@example.com", password="Pass123456!")
        self.carol = User.objects.create_user(username="carol", email="carol@example.com", password="Pass123456!")
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

    def test_workspace_sent_invitations_admin_only(self):
        ws = create_workspace_with_creator(creator=self.user, name="InvWS", description="")
        Invitation.objects.create(
            inviter=self.user,
            invitee=self.bob,
            invitee_email="bob@example.com",
            workspace_id=ws.id,
            status=Invitation.Status.PENDING,
        )

        res = self.client.get(reverse("workspace-invitations", kwargs={"workspace_id": ws.id}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["invitee_email"], "bob@example.com")

        bob_token = self.client.post(
            reverse("login"), {"username": "bob", "password": "Pass123456!"}, format="json"
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {bob_token}")
        forbidden = self.client.get(reverse("workspace-invitations", kwargs={"workspace_id": ws.id}))
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_creator_admin_cannot_demote_creator_or_other_admin(self):
        workspace = self.client.post(reverse("workspace-list-create"), {"name": "WS"}, format="json").data
        wid = workspace["id"]
        WorkspaceMembership.objects.create(workspace_id=wid, user=self.bob, role="member")
        WorkspaceMembership.objects.create(workspace_id=wid, user=self.carol, role="member")
        self.client.patch(
            reverse("workspace-member-role", kwargs={"workspace_id": wid, "user_id": self.bob.pk}),
            {"role": "admin"},
            format="json",
        )
        self.client.patch(
            reverse("workspace-member-role", kwargs={"workspace_id": wid, "user_id": self.carol.pk}),
            {"role": "admin"},
            format="json",
        )

        bob_token = self.client.post(
            reverse("login"), {"username": "bob", "password": "Pass123456!"}, format="json"
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {bob_token}")

        demote_creator = self.client.patch(
            reverse("workspace-member-role", kwargs={"workspace_id": wid, "user_id": self.user.pk}),
            {"role": "member"},
            format="json",
        )
        self.assertEqual(demote_creator.status_code, status.HTTP_403_FORBIDDEN)

        demote_carol = self.client.patch(
            reverse("workspace-member-role", kwargs={"workspace_id": wid, "user_id": self.carol.pk}),
            {"role": "member"},
            format="json",
        )
        self.assertEqual(demote_carol.status_code, status.HTTP_403_FORBIDDEN)

        remove_creator = self.client.delete(
            reverse("workspace-member-delete", kwargs={"workspace_id": wid, "user_id": self.user.pk})
        )
        self.assertEqual(remove_creator.status_code, status.HTTP_403_FORBIDDEN)

    def test_creator_can_demote_other_admin(self):
        workspace = self.client.post(reverse("workspace-list-create"), {"name": "WS"}, format="json").data
        wid = workspace["id"]
        WorkspaceMembership.objects.create(workspace_id=wid, user=self.bob, role="member")
        self.client.patch(
            reverse("workspace-member-role", kwargs={"workspace_id": wid, "user_id": self.bob.pk}),
            {"role": "admin"},
            format="json",
        )

        demote = self.client.patch(
            reverse("workspace-member-role", kwargs={"workspace_id": wid, "user_id": self.bob.pk}),
            {"role": "member"},
            format="json",
        )
        self.assertEqual(demote.status_code, status.HTTP_200_OK)
        self.assertEqual(demote.data["role"], "member")

    def test_admin_cannot_demote_own_admin_role(self):
        workspace = self.client.post(reverse("workspace-list-create"), {"name": "WS"}, format="json").data
        wid = workspace["id"]
        WorkspaceMembership.objects.create(workspace_id=wid, user=self.bob, role="member")
        self.client.patch(
            reverse("workspace-member-role", kwargs={"workspace_id": wid, "user_id": self.bob.pk}),
            {"role": "admin"},
            format="json",
        )

        bob_token = self.client.post(
            reverse("login"), {"username": "bob", "password": "Pass123456!"}, format="json"
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {bob_token}")

        self_demote = self.client.patch(
            reverse("workspace-member-role", kwargs={"workspace_id": wid, "user_id": self.bob.pk}),
            {"role": "member"},
            format="json",
        )
        self.assertEqual(self_demote.status_code, status.HTTP_403_FORBIDDEN)

    def test_creator_can_delete_workspace(self):
        workspace = self.client.post(reverse("workspace-list-create"), {"name": "Deletable"}, format="json").data
        wid = workspace["id"]
        delete_res = self.client.delete(reverse("workspace-detail", kwargs={"workspace_id": wid}))
        self.assertEqual(delete_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Workspace.objects.filter(pk=wid).exists())

    def test_non_creator_admin_cannot_delete_workspace(self):
        workspace = self.client.post(reverse("workspace-list-create"), {"name": "WS"}, format="json").data
        wid = workspace["id"]
        WorkspaceMembership.objects.create(workspace_id=wid, user=self.bob, role="member")
        self.client.patch(
            reverse("workspace-member-role", kwargs={"workspace_id": wid, "user_id": self.bob.pk}),
            {"role": "admin"},
            format="json",
        )

        bob_token = self.client.post(
            reverse("login"), {"username": "bob", "password": "Pass123456!"}, format="json"
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {bob_token}")

        delete_res = self.client.delete(reverse("workspace-detail", kwargs={"workspace_id": wid}))
        self.assertEqual(delete_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Workspace.objects.filter(pk=wid).exists())

    def test_non_member_cannot_delete_workspace(self):
        ws = create_workspace_with_creator(creator=self.user, name="PrivateWS", description="")
        bob_token = self.client.post(
            reverse("login"), {"username": "bob", "password": "Pass123456!"}, format="json"
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {bob_token}")

        delete_res = self.client.delete(reverse("workspace-detail", kwargs={"workspace_id": ws.id}))
        self.assertEqual(delete_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Workspace.objects.filter(pk=ws.id).exists())
