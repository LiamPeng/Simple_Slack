from django.db.models import Q
from rest_framework import serializers

from backend.apps.channels.models import Channel
from backend.apps.channels.serializers import ChannelSerializer

from .models import Workspace, WorkspaceMembership


class WorkspaceMembershipSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = WorkspaceMembership
        fields = ["id", "user_id", "username", "email", "role", "joined_at"]


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ["id", "name", "description", "creator", "created_at"]
        read_only_fields = ["id", "creator", "created_at"]


class WorkspaceDetailSerializer(WorkspaceSerializer):
    members = serializers.SerializerMethodField()
    channels = serializers.SerializerMethodField()

    class Meta(WorkspaceSerializer.Meta):
        fields = WorkspaceSerializer.Meta.fields + ["members", "channels"]

    def get_members(self, obj):
        memberships = obj.memberships.select_related("user").all()
        return WorkspaceMembershipSerializer(memberships, many=True).data

    def get_channels(self, obj):
        request = self.context.get("request")
        qs = Channel.objects.filter(workspace=obj).select_related("creator").prefetch_related("memberships__user")
        if request and request.user.is_authenticated:
            qs = qs.filter(
                Q(channel_type=Channel.ChannelType.PUBLIC) | Q(memberships__user=request.user)
            ).distinct()
        return ChannelSerializer(qs, many=True, context={"request": request}).data


class CreateWorkspaceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    description = serializers.CharField(required=False, allow_blank=True)


class UpdateWorkspaceMemberRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=WorkspaceMembership.Role.choices)
