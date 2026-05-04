import json
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.http import Http404
from django.shortcuts import aget_object_or_404

from backend.apps.channels.models import Channel
from backend.apps.core.access import can_access_channel

from .realtime import chat_group_name
from .ws_auth import user_from_access_token


class ChannelChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        query = parse_qs(self.scope.get("query_string", b"").decode())
        token = (query.get("token") or [None])[0]

        user = await sync_to_async(user_from_access_token)(token)
        if user is None or not user.is_authenticated:
            await self.close(code=4001)
            return

        try:
            channel = await aget_object_or_404(Channel, pk=self.channel_id)
        except Http404:
            await self.close(code=4404)
            return

        if not await sync_to_async(can_access_channel)(user, channel):
            await self.close(code=4403)
            return

        self.group_name = chat_group_name(self.channel_id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if getattr(self, "group_name", None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["payload"]))
