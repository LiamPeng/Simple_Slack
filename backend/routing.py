from django.urls import path

from backend.apps.messages.consumers import ChannelChatConsumer

websocket_urlpatterns = [
    path("ws/channel/<int:channel_id>/", ChannelChatConsumer.as_asgi()),
]
