from django.urls import path

from .views import ChannelMessagesView, SearchMessagesView

urlpatterns = [
    path("channels/<int:channel_id>/messages/", ChannelMessagesView.as_view(), name="channel-messages"),
    path("search/", SearchMessagesView.as_view(), name="message-search"),
]
