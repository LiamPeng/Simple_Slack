from django.urls import path

from .views import WorkspaceDetailView, WorkspaceListCreateView

urlpatterns = [
    path("", WorkspaceListCreateView.as_view(), name="workspace-list-create"),
    path("<int:workspace_id>/", WorkspaceDetailView.as_view(), name="workspace-detail"),
]
