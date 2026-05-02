from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from backend.apps.channels.models import ChannelMembership
from backend.apps.core.access import is_workspace_admin

from .models import Invitation

User = get_user_model()


def create_invitation(*, inviter, workspace, invitee_email, channel=None):
    if not is_workspace_admin(inviter, workspace):
        raise PermissionError("Only workspace admins can invite users")

    invitee = User.objects.filter(email__iexact=invitee_email).first()
    return Invitation.objects.create(
        inviter=inviter,
        invitee_email=invitee_email.strip().lower(),
        invitee=invitee,
        workspace=workspace,
        channel=channel,
    )


@transaction.atomic
def accept_invitation(*, invitation, user):
    if invitation.invitee_id and invitation.invitee_id != user.id:
        raise PermissionError("Only invitee can accept invitation")
    if invitation.invitee_email.lower() != user.email.lower():
        raise PermissionError("Invitation email does not match your account")
    if invitation.status != Invitation.Status.PENDING:
        raise ValueError("Invitation already handled")

    invitation.invitee = user
    invitation.status = Invitation.Status.ACCEPTED
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["invitee", "status", "responded_at"])

    from backend.apps.workspaces.models import WorkspaceMembership

    WorkspaceMembership.objects.get_or_create(
        workspace=invitation.workspace,
        user=user,
        defaults={"role": WorkspaceMembership.Role.MEMBER},
    )

    if invitation.channel_id:
        ChannelMembership.objects.get_or_create(channel=invitation.channel, user=user)


@transaction.atomic
def reject_invitation(*, invitation, user):
    if invitation.invitee_id and invitation.invitee_id != user.id:
        raise PermissionError("Only invitee can reject invitation")
    if invitation.invitee_email.lower() != user.email.lower():
        raise PermissionError("Invitation email does not match your account")
    if invitation.status != Invitation.Status.PENDING:
        raise ValueError("Invitation already handled")

    invitation.invitee = user
    invitation.status = Invitation.Status.DECLINED
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["invitee", "status", "responded_at"])


def cancel_pending_invitation(*, invitation, actor):
    """Workspace admin revokes a pending invitation (row deleted)."""
    if not is_workspace_admin(actor, invitation.workspace):
        raise PermissionError("Only workspace admins can cancel invitations")
    if invitation.status != Invitation.Status.PENDING:
        raise ValueError("Only pending invitations can be cancelled")
    invitation.delete()
