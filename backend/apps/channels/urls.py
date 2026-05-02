from django.urls import path

from .views import (
    ChannelDetailView,
    WorkspaceChannelCreateView,
    WorkspaceDirectChannelCreateView,
    WorkspaceDirectChannelGetOrCreateView,
)

urlpatterns = [
    path("workspaces/<int:workspace_id>/channels/", WorkspaceChannelCreateView.as_view(), name="workspace-channel-create"),
    path(
        "workspaces/<int:workspace_id>/direct-channels/",
        WorkspaceDirectChannelCreateView.as_view(),
        name="workspace-direct-channel-create",
    ),
    path(
        "workspaces/<int:workspace_id>/direct-channels/get-or-create/",
        WorkspaceDirectChannelGetOrCreateView.as_view(),
        name="workspace-direct-channel-get-or-create",
    ),
    path("channels/<int:channel_id>/", ChannelDetailView.as_view(), name="channel-detail"),
]
