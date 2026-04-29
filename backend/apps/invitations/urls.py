from django.urls import path

from .views import InvitationAcceptView, InvitationListView, InvitationRejectView, WorkspaceInviteView

urlpatterns = [
    path("invitations/", InvitationListView.as_view(), name="invitation-list"),
    path("workspaces/<int:workspace_id>/invite/", WorkspaceInviteView.as_view(), name="workspace-invite"),
    path("invitations/<int:invitation_id>/accept/", InvitationAcceptView.as_view(), name="invitation-accept"),
    path("invitations/<int:invitation_id>/reject/", InvitationRejectView.as_view(), name="invitation-reject"),
]
