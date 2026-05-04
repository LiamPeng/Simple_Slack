from django.conf import settings
from django.db import models
from django.db.models import Q


class Invitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_invitations")
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_invitations",
        null=True,
        blank=True,
    )
    invitee_email = models.EmailField()
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE, related_name="invitations")
    channel = models.ForeignKey(
        "slack_channels.Channel",
        on_delete=models.CASCADE,
        related_name="invitations",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True, db_column="invited_at")
    responded_at = models.DateTimeField(null=True, blank=True)
    last_notified_at = models.DateTimeField(null=True, blank=True)
    notification_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "WorkspaceInvitation"
        constraints = [
            models.UniqueConstraint(
                fields=["invitee_email", "workspace", "channel"],
                condition=Q(status="pending"),
                name="uniq_pending_invitation",
            ),
        ]

    def __str__(self):
        return f"{self.inviter_id}->{self.invitee_id}"
