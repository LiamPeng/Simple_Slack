from django.conf import settings
from django.db import models
from django.db.models import Q


class Invitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_invitations")
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_invitations")
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE, related_name="invitations")
    channel = models.ForeignKey("channels.Channel", on_delete=models.CASCADE, related_name="invitations", null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["invitee", "workspace", "channel"],
                condition=Q(status="pending"),
                name="uniq_pending_invitation",
            ),
        ]

    def __str__(self):
        return f"{self.inviter_id}->{self.invitee_id}"
