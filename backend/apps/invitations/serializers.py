from rest_framework import serializers

from .models import Invitation


class InvitationSerializer(serializers.ModelSerializer):
    inviter_username = serializers.CharField(source="inviter.username", read_only=True)
    invitee_username = serializers.CharField(source="invitee.username", read_only=True, allow_null=True)
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)

    class Meta:
        model = Invitation
        fields = [
            "id",
            "inviter",
            "inviter_username",
            "invitee",
            "invitee_username",
            "invitee_email",
            "workspace",
            "workspace_name",
            "channel",
            "status",
            "created_at",
            "responded_at",
            "last_notified_at",
            "notification_count",
        ]
        read_only_fields = [
            "id",
            "inviter",
            "status",
            "created_at",
            "responded_at",
            "last_notified_at",
            "notification_count",
        ]


class CreateInvitationSerializer(serializers.Serializer):
    invitee_email = serializers.EmailField()
    channel_id = serializers.IntegerField(required=False)
