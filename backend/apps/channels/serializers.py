from rest_framework import serializers

from .models import Channel, ChannelMembership


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ["id", "workspace", "name", "channel_type", "creator", "created_at"]
        read_only_fields = ["id", "creator", "created_at", "workspace"]


class ChannelMembershipSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ChannelMembership
        fields = ["id", "user_id", "username", "joined_at"]


class CreateChannelSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    channel_type = serializers.ChoiceField(choices=Channel.ChannelType.choices)
