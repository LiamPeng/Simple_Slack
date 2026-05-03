from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from backend.apps.core.access import is_workspace_admin

from .models import Invitation


RESEND_WAIT = timedelta(days=5)


def _can_manage_invitation_notification(actor, invitation):
    ws = invitation.workspace
    if is_workspace_admin(actor, ws):
        return True
    if invitation.channel_id and invitation.channel.creator_id == actor.id:
        return True
    return False


@transaction.atomic
def resend_invitation_notification(*, invitation, actor):
    if not _can_manage_invitation_notification(actor, invitation):
        raise PermissionError("Only workspace admins or the channel creator can resend invitations")
    if invitation.status != Invitation.Status.PENDING:
        raise ValueError("Only pending invitations can be resent")
    if invitation.created_at > timezone.now() - RESEND_WAIT:
        raise ValueError("Invitation can only be resent after five days")

    invitation.last_notified_at = timezone.now()
    invitation.notification_count += 1
    invitation.save(update_fields=["last_notified_at", "notification_count"])
    return invitation
