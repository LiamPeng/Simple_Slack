from rest_framework import serializers

from .models import Invitation


class InvitationSerializer(serializers.ModelSerializer):
    inviter_username = serializers.CharField(source="inviter.username", read_only=True)
    invitee_username = serializers.CharField(source="invitee.username", read_only=True)

    class Meta:
        model = Invitation
        fields = [
            "id",
            "inviter",
            "inviter_username",
            "invitee",
            "invitee_username",
            "workspace",
            "channel",
            "status",
            "created_at",
            "responded_at",
        ]
        read_only_fields = ["id", "inviter", "status", "created_at", "responded_at"]


class CreateInvitationSerializer(serializers.Serializer):
    invitee_username = serializers.CharField(max_length=150)
    channel_id = serializers.IntegerField(required=False)
