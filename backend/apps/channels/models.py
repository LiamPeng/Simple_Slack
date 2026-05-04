from django.conf import settings
from django.db import models


class Channel(models.Model):
    class ChannelType(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        DIRECT = "direct", "Direct"

    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE, related_name="channels")
    name = models.CharField(max_length=120)
    channel_type = models.CharField(max_length=16, choices=ChannelType.choices, default=ChannelType.PUBLIC)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_channels")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Keep legacy table name so DBs created under app label ``channels`` still match the ORM
        # after the label was changed to ``slack_channels`` (Django Channels name collision).
        db_table = "channels_channel"
        constraints = [
            models.UniqueConstraint(fields=["workspace", "name"], name="uniq_workspace_channel_name"),
        ]

    def __str__(self):
        return f"{self.workspace_id}:{self.name}"


class ChannelMembership(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="channel_memberships")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "channels_channelmembership"
        constraints = [
            models.UniqueConstraint(fields=["channel", "user"], name="uniq_channel_user_membership"),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.channel_id}"


