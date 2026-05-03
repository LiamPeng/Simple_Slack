from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from backend.apps.channels.models import Channel, ChannelMembership
from backend.apps.core.access import is_workspace_admin
from backend.apps.workspaces.models import WorkspaceMembership

from .models import Invitation

User = get_user_model()


@transaction.atomic
def create_invitation(*, inviter, workspace, invitee_email, channel=None):
    if channel is not None:
        if channel.workspace_id != workspace.id:
            raise ValueError("Channel must belong to the invited workspace")
        if channel.channel_type != Channel.ChannelType.PRIVATE:
            raise ValueError("Channel invitations are only supported for private channels")
        if channel.creator_id != inviter.id:
            raise PermissionError("Only the channel creator can invite users to this private channel")
        if not WorkspaceMembership.objects.filter(workspace=workspace, user=inviter).exists():
            raise PermissionError("Inviter must be a workspace member")
    else:
        if not is_workspace_admin(inviter, workspace):
            raise PermissionError("Only workspace admins can invite users to the workspace")

    invitee = User.objects.filter(email__iexact=invitee_email).first()
    if invitee and channel is None:
        if WorkspaceMembership.objects.filter(workspace=workspace, user=invitee).exists():
            raise ValueError("User is already a workspace member")
    if invitee and channel:
        if ChannelMembership.objects.filter(channel=channel, user=invitee).exists():
            raise ValueError("User is already a channel member")

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
    """Deletes a pending invitation (workspace admin or private-channel creator)."""
    if invitation.status != Invitation.Status.PENDING:
        raise ValueError("Only pending invitations can be cancelled")
    workspace = invitation.workspace
    if is_workspace_admin(actor, workspace):
        invitation.delete()
        return
    if invitation.channel_id:
        ch = invitation.channel
        if ch.creator_id == actor.id:
            invitation.delete()
            return
    raise PermissionError("Only workspace admins or the channel creator can cancel this invitation")
