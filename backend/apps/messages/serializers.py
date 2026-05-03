from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Message

User = get_user_model()


class MessageSenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class MessageSerializer(serializers.ModelSerializer):
    sender = MessageSenderSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "channel", "sender", "body", "created_at"]
        read_only_fields = ["id", "sender", "created_at", "channel"]


class CreateMessageSerializer(serializers.Serializer):
    body = serializers.CharField()

    def validate_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty")
        return value
