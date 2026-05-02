from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.core.access import can_access_channel, is_workspace_member
from backend.apps.workspaces.models import Workspace

from .models import Channel
from .serializers import ChannelMembershipSerializer, ChannelSerializer, CreateChannelSerializer
from .services import create_channel_with_creator


class WorkspaceChannelCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not is_workspace_member(request.user, workspace):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateChannelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        channel = create_channel_with_creator(
            workspace=workspace,
            creator=request.user,
            name=serializer.validated_data["name"],
            channel_type=serializer.validated_data["channel_type"],
        )
        return Response(ChannelSerializer(channel).data, status=status.HTTP_201_CREATED)


class ChannelDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        if not can_access_channel(request.user, channel):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        payload = ChannelSerializer(channel).data
        payload["members"] = ChannelMembershipSerializer(channel.memberships.select_related("user"), many=True).data
        payload["messages"] = list(
            channel.messages.select_related("sender").values(
                "id", "sender_id", "sender__username", "body", "created_at"
            )
        )
        return Response(payload)
