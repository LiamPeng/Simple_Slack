from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.core.access import is_workspace_member

from .models import Workspace
from .serializers import CreateWorkspaceSerializer, WorkspaceDetailSerializer, WorkspaceSerializer
from .services import create_workspace_with_creator


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
