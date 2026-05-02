from rest_framework import serializers

from .models import Channel, ChannelMembership


class ChannelSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = ["id", "workspace", "name", "channel_type", "creator", "created_at", "other_user"]
        read_only_fields = ["id", "creator", "created_at", "workspace"]

    def get_other_user(self, obj):
        request = self.context.get("request")
        if obj.channel_type != Channel.ChannelType.DIRECT or request is None:
            return None

        membership = obj.memberships.select_related("user").exclude(user=request.user).first()
        if not membership:
            return None

        return {
            "id": membership.user.id,
            "username": membership.user.username,
            "email": membership.user.email,
        }


class ChannelMembershipSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ChannelMembership
        fields = ["id", "user_id", "username", "joined_at"]


class CreateChannelSerializer(serializers.Serializer):
    CHANNEL_CREATE_CHOICES = [
        Channel.ChannelType.PUBLIC,
        Channel.ChannelType.PRIVATE,
    ]

    name = serializers.CharField(max_length=120, trim_whitespace=True, allow_blank=False)
    channel_type = serializers.ChoiceField(choices=CHANNEL_CREATE_CHOICES)


class DirectChannelSerializer(serializers.Serializer):
    other_user_id = serializers.IntegerField()
