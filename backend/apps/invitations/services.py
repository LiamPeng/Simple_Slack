from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from backend.apps.channels.models import ChannelMembership
from backend.apps.core.access import is_workspace_admin

from .models import Invitation

User = get_user_model()


def create_invitation(*, inviter, workspace, invitee_username, channel=None):
    if not is_workspace_admin(inviter, workspace):
        raise PermissionError("Only workspace admins can invite users")

    invitee = User.objects.get(username=invitee_username)
    return Invitation.objects.create(
        inviter=inviter,
        invitee=invitee,
        workspace=workspace,
        channel=channel,
    )


@transaction.atomic
def accept_invitation(*, invitation, user):
    if invitation.invitee_id != user.id:
        raise PermissionError("Only invitee can accept invitation")
    if invitation.status != Invitation.Status.PENDING:
        raise ValueError("Invitation already handled")

    invitation.status = Invitation.Status.ACCEPTED
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["status", "responded_at"])

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
    if invitation.invitee_id != user.id:
        raise PermissionError("Only invitee can reject invitation")
    if invitation.status != Invitation.Status.PENDING:
        raise ValueError("Invitation already handled")

    invitation.status = Invitation.Status.REJECTED
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["status", "responded_at"])
