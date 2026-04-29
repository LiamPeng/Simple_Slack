from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "channel", "sender", "sender_username", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "sender", "created_at", "updated_at", "channel", "sender_username"]


class CreateMessageSerializer(serializers.Serializer):
    content = serializers.CharField()

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty")
        return value
