from django.urls import path

from .views import ChannelDetailView, WorkspaceChannelCreateView

urlpatterns = [
    path("workspaces/<int:workspace_id>/channels/", WorkspaceChannelCreateView.as_view(), name="workspace-channel-create"),
    path("channels/<int:channel_id>/", ChannelDetailView.as_view(), name="channel-detail"),
]
