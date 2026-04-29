from django.conf import settings
from django.db import models


class Workspace(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_workspaces")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class WorkspaceMembership(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workspace_memberships")
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["workspace", "user"], name="uniq_workspace_user_membership"),
        ]

    def __str__(self):
        return f"{self.user} @ {self.workspace}"
