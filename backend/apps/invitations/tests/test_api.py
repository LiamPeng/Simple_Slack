from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import timedelta

from backend.apps.channels.models import Channel, ChannelMembership
from backend.apps.invitations.models import Invitation
from backend.apps.invitations.services import create_invitation
from backend.apps.workspaces.models import WorkspaceMembership
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

    def test_non_workspace_member_cannot_send_invitation(self):
        User.objects.create_user(username="outsider", email="outsider@example.com", password="Pass123456!")
        self._auth("outsider", "Pass123456!")
        res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "anyone@example.com"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_cannot_invite_existing_workspace_member(self):
        WorkspaceMembership.objects.create(workspace=self.workspace, user=self.bob)
        self._auth("alice", "Pass123456!")

        invite_res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "bob@example.com"},
            format="json",
        )

        self.assertEqual(invite_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Invitation.objects.count(), 0)

    def test_cannot_invite_existing_channel_member(self):
        channel = Channel.objects.create(
            workspace=self.workspace,
            creator=self.alice,
            name="private",
            channel_type=Channel.ChannelType.PRIVATE,
        )
        ChannelMembership.objects.create(channel=channel, user=self.bob)
        self._auth("alice", "Pass123456!")

        invite_res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "bob@example.com", "channel_id": channel.id},
            format="json",
        )

        self.assertEqual(invite_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Invitation.objects.count(), 0)

    def test_service_rejects_channel_from_different_workspace(self):
        other_workspace = create_workspace_with_creator(creator=self.bob, name="Other", description="")
        channel = Channel.objects.create(
            workspace=other_workspace,
            creator=self.bob,
            name="other-private",
            channel_type=Channel.ChannelType.PRIVATE,
        )

        with self.assertRaises(ValueError):
            create_invitation(
                inviter=self.alice,
                workspace=self.workspace,
                invitee_email="new-person@example.com",
                channel=channel,
            )

    def test_admin_can_resend_old_pending_invitation(self):
        invitation = Invitation.objects.create(
            inviter=self.alice,
            invitee=self.bob,
            invitee_email="bob@example.com",
            workspace=self.workspace,
            status=Invitation.Status.PENDING,
        )
        old_created_at = timezone.now() - timedelta(days=6)
        Invitation.objects.filter(pk=invitation.pk).update(created_at=old_created_at)
        self._auth("alice", "Pass123456!")

        resend_res = self.client.post(
            reverse("invitation-resend", kwargs={"invitation_id": invitation.id}),
            {},
            format="json",
        )

        self.assertEqual(resend_res.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertIsNotNone(invitation.last_notified_at)
        self.assertEqual(invitation.notification_count, 1)

    def test_admin_cannot_resend_new_pending_invitation(self):
        invitation = Invitation.objects.create(
            inviter=self.alice,
            invitee=self.bob,
            invitee_email="bob@example.com",
            workspace=self.workspace,
            status=Invitation.Status.PENDING,
        )
        self._auth("alice", "Pass123456!")

        resend_res = self.client.post(
            reverse("invitation-resend", kwargs={"invitation_id": invitation.id}),
            {},
            format="json",
        )

        self.assertEqual(resend_res.status_code, status.HTTP_400_BAD_REQUEST)
        invitation.refresh_from_db()
        self.assertIsNone(invitation.last_notified_at)
        self.assertEqual(invitation.notification_count, 0)

    def test_non_admin_cannot_resend_pending_invitation(self):
        invitation = Invitation.objects.create(
            inviter=self.alice,
            invitee=self.bob,
            invitee_email="bob@example.com",
            workspace=self.workspace,
            status=Invitation.Status.PENDING,
        )
        old_created_at = timezone.now() - timedelta(days=6)
        Invitation.objects.filter(pk=invitation.pk).update(created_at=old_created_at)
        self._auth("bob", "Pass123456!")

        resend_res = self.client.post(
            reverse("invitation-resend", kwargs={"invitation_id": invitation.id}),
            {},
            format="json",
        )

        self.assertEqual(resend_res.status_code, status.HTTP_403_FORBIDDEN)

    def test_private_channel_creator_member_can_invite(self):
        WorkspaceMembership.objects.create(workspace=self.workspace, user=self.bob, role="member")
        self._auth("bob", "Pass123456!")
        ch_res = self.client.post(
            reverse("workspace-channel-create", kwargs={"workspace_id": self.workspace.id}),
            {"name": "hiring", "channel_type": "private"},
            format="json",
        )
        self.assertEqual(ch_res.status_code, status.HTTP_201_CREATED)
        channel_id = ch_res.data["id"]

        invite_res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "carol@example.com", "channel_id": channel_id},
            format="json",
        )
        self.assertEqual(invite_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(invite_res.data["channel"], channel_id)

    def test_workspace_admin_non_creator_cannot_invite_to_private_channel(self):
        WorkspaceMembership.objects.create(workspace=self.workspace, user=self.bob, role="member")
        self._auth("bob", "Pass123456!")
        ch_res = self.client.post(
            reverse("workspace-channel-create", kwargs={"workspace_id": self.workspace.id}),
            {"name": "committee", "channel_type": "private"},
            format="json",
        )
        self.assertEqual(ch_res.status_code, status.HTTP_201_CREATED)
        channel_id = ch_res.data["id"]

        self._auth("alice", "Pass123456!")
        invite_res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "carol@example.com", "channel_id": channel_id},
            format="json",
        )
        self.assertEqual(invite_res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_attach_public_channel_to_invitation(self):
        channel = Channel.objects.create(
            workspace=self.workspace,
            creator=self.alice,
            name="general",
            channel_type=Channel.ChannelType.PUBLIC,
        )
        ChannelMembership.objects.create(channel=channel, user=self.alice)
        self._auth("alice", "Pass123456!")
        invite_res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "carol@example.com", "channel_id": channel.id},
            format="json",
        )
        self.assertEqual(invite_res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_private_channel_creator_can_cancel_own_pending_channel_invitation(self):
        WorkspaceMembership.objects.create(workspace=self.workspace, user=self.bob, role="member")
        self._auth("bob", "Pass123456!")
        ch_res = self.client.post(
            reverse("workspace-channel-create", kwargs={"workspace_id": self.workspace.id}),
            {"name": "promotions", "channel_type": "private"},
            format="json",
        )
        cid = ch_res.data["id"]
        invite_res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "dana@example.com", "channel_id": cid},
            format="json",
        )
        self.assertEqual(invite_res.status_code, status.HTTP_201_CREATED)
        inv_id = invite_res.data["id"]

        cancel_res = self.client.post(reverse("invitation-cancel", kwargs={"invitation_id": inv_id}), {}, format="json")
        self.assertEqual(cancel_res.status_code, status.HTTP_204_NO_CONTENT)

    def test_workspace_admin_can_cancel_another_users_private_channel_invitation(self):
        WorkspaceMembership.objects.create(workspace=self.workspace, user=self.bob, role="member")
        self._auth("bob", "Pass123456!")
        ch_res = self.client.post(
            reverse("workspace-channel-create", kwargs={"workspace_id": self.workspace.id}),
            {"name": "secret", "channel_type": "private"},
            format="json",
        )
        cid = ch_res.data["id"]
        invite_res = self.client.post(
            reverse("workspace-invite", kwargs={"workspace_id": self.workspace.id}),
            {"invitee_email": "dana@example.com", "channel_id": cid},
            format="json",
        )
        inv_id = invite_res.data["id"]

        self._auth("alice", "Pass123456!")
        cancel_res = self.client.post(reverse("invitation-cancel", kwargs={"invitation_id": inv_id}), {}, format="json")
        self.assertEqual(cancel_res.status_code, status.HTTP_204_NO_CONTENT)

    def test_channel_creator_can_resend_old_private_channel_invitation(self):
        WorkspaceMembership.objects.create(workspace=self.workspace, user=self.bob, role="member")
        channel = Channel.objects.create(
            workspace=self.workspace,
            creator=self.bob,
            name="private-only",
            channel_type=Channel.ChannelType.PRIVATE,
        )
        ChannelMembership.objects.create(channel=channel, user=self.bob)
        invitation = Invitation.objects.create(
            inviter=self.bob,
            invitee=None,
            invitee_email="remote@example.com",
            workspace=self.workspace,
            channel=channel,
            status=Invitation.Status.PENDING,
        )
        old_created_at = timezone.now() - timedelta(days=6)
        Invitation.objects.filter(pk=invitation.pk).update(created_at=old_created_at)
        self._auth("bob", "Pass123456!")

        resend_res = self.client.post(
            reverse("invitation-resend", kwargs={"invitation_id": invitation.id}),
            {},
            format="json",
        )
        self.assertEqual(resend_res.status_code, status.HTTP_200_OK)
