from django.urls import path

from .views import (
    WorkspaceDetailView,
    WorkspaceListCreateView,
    WorkspaceMemberDeleteView,
    WorkspaceMemberRoleView,
)

urlpatterns = [
    path("", WorkspaceListCreateView.as_view(), name="workspace-list-create"),
    path("<int:workspace_id>/", WorkspaceDetailView.as_view(), name="workspace-detail"),
    path("<int:workspace_id>/members/<int:user_id>/role/", WorkspaceMemberRoleView.as_view(), name="workspace-member-role"),
    path("<int:workspace_id>/members/<int:user_id>/", WorkspaceMemberDeleteView.as_view(), name="workspace-member-delete"),
]
