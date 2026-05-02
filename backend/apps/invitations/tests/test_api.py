from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.invitations.models import Invitation
from backend.apps.workspaces.services import create_workspace_with_creator


User = get_user_model()


class InvitationApiTests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", email="alice@example.com", password="Pass123456!")
        self.bob = User.objects.create_user(username="bob", email="bob@example.com", password="Pass123456!")
        self.workspace = create_workspace_with_creator(creator=self.alice, name="WS", description="")

    def _auth(self, username, password):
        token = self.client.post(reverse("login"), {"username": username, "password": password}, format="json").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_invite_and_accept(self):
        self._auth("alice", "Pass123456!")
        invite_res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "bob@example.com"},
            format="json",
        )
        self.assertEqual(invite_res.status_code, status.HTTP_201_CREATED)

        self._auth("bob", "Pass123456!")
        accept_res = self.client.post(
            reverse("invitation-accept", kwargs={"invitation_id": invite_res.data["id"]}),
            {},
            format="json",
        )
        self.assertEqual(accept_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Invitation.objects.get(pk=invite_res.data["id"]).status, Invitation.Status.ACCEPTED)

    def test_invite_before_signup_links_to_new_user(self):
        self._auth("alice", "Pass123456!")
        invite_res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "new-user@example.com"},
            format="json",
        )
        self.assertEqual(invite_res.status_code, status.HTTP_201_CREATED)
        invitation = Invitation.objects.get(pk=invite_res.data["id"])
        self.assertIsNone(invitation.invitee)

        register_res = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "new-user@example.com",
                "nickname": "New User",
                "password": "Pass123456!",
            },
            format="json",
        )
        self.assertEqual(register_res.status_code, status.HTTP_201_CREATED)

        invitation.refresh_from_db()
        self.assertIsNotNone(invitation.invitee)
        self.assertEqual(invitation.invitee.email, "new-user@example.com")

    def test_invitee_sees_invitation_matched_by_linked_user_not_only_email(self):
        """Pending invites should appear when invitee FK matches, even if invitee_email drifts."""
        inv = Invitation.objects.create(
            inviter=self.alice,
            invitee=self.bob,
            invitee_email="legacy-or-wrong@example.com",
            workspace=self.workspace,
            status=Invitation.Status.PENDING,
        )
        self._auth("bob", "Pass123456!")
        list_res = self.client.get(reverse("invitation-list"))
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        ids = [row["id"] for row in list_res.data]
        self.assertIn(inv.id, ids)

    def test_admin_can_cancel_pending_invitation(self):
        self._auth("alice", "Pass123456!")
        invite_res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "bob@example.com"},
            format="json",
        )
        self.assertEqual(invite_res.status_code, status.HTTP_201_CREATED)
        inv_id = invite_res.data["id"]

        cancel_res = self.client.post(reverse("invitation-cancel", kwargs={"invitation_id": inv_id}), {}, format="json")
        self.assertEqual(cancel_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Invitation.objects.filter(pk=inv_id).exists())

    def test_non_admin_cannot_cancel_workspace_invitation(self):
        self._auth("alice", "Pass123456!")
        invite_res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "bob@example.com"},
            format="json",
        )
        self.assertEqual(invite_res.status_code, status.HTTP_201_CREATED)
        inv_id = invite_res.data["id"]

        self._auth("bob", "Pass123456!")
        cancel_res = self.client.post(reverse("invitation-cancel", kwargs={"invitation_id": inv_id}), {}, format="json")
        self.assertEqual(cancel_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Invitation.objects.filter(pk=inv_id).exists())
