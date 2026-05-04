from django.urls import path

from .views import ChannelMessagesView, MarkChannelReadView, SearchMessagesView

urlpatterns = [
    path("channels/<int:channel_id>/messages/", ChannelMessagesView.as_view(), name="channel-messages"),
    path("channels/<int:channel_id>/read/", MarkChannelReadView.as_view(), name="channel-mark-read"),
    path("search/", SearchMessagesView.as_view(), name="message-search"),
]
