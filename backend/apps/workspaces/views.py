from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.core.access import is_workspace_admin, is_workspace_member
from backend.apps.invitations.models import Invitation
from backend.apps.invitations.serializers import InvitationSerializer

from .models import Workspace
from .serializers import (
    CreateWorkspaceSerializer,
    UpdateWorkspaceMemberRoleSerializer,
    WorkspaceDetailSerializer,
    WorkspaceMembershipSerializer,
    WorkspaceSerializer,
)
from .services import create_workspace_with_creator, delete_workspace, remove_workspace_member, set_member_role


class WorkspaceListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Workspace.objects.filter(memberships__user=request.user).distinct()
        return Response(WorkspaceSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = CreateWorkspaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        workspace = create_workspace_with_creator(
            creator=request.user,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )
        return Response(WorkspaceSerializer(workspace).data, status=status.HTTP_201_CREATED)


class WorkspaceDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not is_workspace_member(request.user, workspace):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        return Response(WorkspaceDetailSerializer(workspace).data)

    def delete(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not is_workspace_member(request.user, workspace):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        try:
            delete_workspace(workspace=workspace, actor=request.user)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkspaceInvitationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not is_workspace_admin(request.user, workspace):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        queryset = Invitation.objects.filter(
            workspace=workspace,
            status=Invitation.Status.PENDING,
        ).select_related("inviter", "workspace").order_by("-created_at")
        return Response(InvitationSerializer(queryset, many=True).data)


class WorkspaceMemberRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, workspace_id, user_id):
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        serializer = UpdateWorkspaceMemberRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            membership = set_member_role(
                workspace=workspace,
                actor=request.user,
                target_user_id=user_id,
                role=serializer.validated_data["role"],
            )
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(WorkspaceMembershipSerializer(membership).data)


class WorkspaceMemberDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, workspace_id, user_id):
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        try:
            remove_workspace_member(
                workspace=workspace,
                actor=request.user,
                target_user_id=user_id,
            )
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
