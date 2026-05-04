"""Channel layer helpers for live message delivery."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def chat_group_name(channel_id: int) -> str:
    return f"chat_{channel_id}"


def broadcast_channel_message(channel_id: int, message_data: dict) -> None:
    """Notify all subscribers in ``chat_<channel_id>`` (same shape as MessageSerializer)."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        chat_group_name(channel_id),
        {"type": "chat.message", "payload": message_data},
    )
