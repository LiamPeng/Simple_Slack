from django.conf import settings
from django.db import models


class Message(models.Model):
    channel = models.ForeignKey("slack_channels.Channel", on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["channel", "created_at"]),
        ]

    def __str__(self):
        return f"{self.sender_id}:{self.channel_id}"
