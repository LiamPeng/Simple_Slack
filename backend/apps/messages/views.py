from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.channels.models import Channel
from backend.apps.core.access import can_access_channel

from .models import Message
from .serializers import CreateMessageSerializer, MessageSerializer


class ChannelMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        if not can_access_channel(request.user, channel):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        queryset = Message.objects.filter(channel=channel).select_related("sender")
        return Response(MessageSerializer(queryset, many=True).data)

    def post(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        if not can_access_channel(request.user, channel):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = Message.objects.create(
            channel=channel,
            sender=request.user,
            body=serializer.validated_data["body"],
        )
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


class SearchMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if not q:
            return Response([])

        queryset = Message.objects.filter(
            Q(channel__channel_type="public", channel__workspace__memberships__user=request.user)
            | Q(channel__memberships__user=request.user),
            body__icontains=q,
        ).select_related("sender", "channel", "channel__workspace").distinct()

        results = [
            {
                "id": m.id,
                "body": m.body,
                "created_at": m.created_at,
                "sender": {"id": m.sender_id, "username": m.sender.username},
                "channel": m.channel_id,
                "channel_name": m.channel.name,
                "workspace_name": m.channel.workspace.name,
            }
            for m in queryset
        ]
        return Response(results)
