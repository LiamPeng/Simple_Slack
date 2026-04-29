from rest_framework.permissions import BasePermission

from backend.apps.core.access import is_workspace_member
from .models import Workspace


class IsWorkspaceMember(BasePermission):
    def has_permission(self, request, view):
        workspace_id = view.kwargs.get("workspace_id") or view.kwargs.get("pk")
        if not workspace_id:
            return True
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            return False
        return is_workspace_member(request.user, workspace)
