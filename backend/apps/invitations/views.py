from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.channels.models import Channel
from backend.apps.workspaces.models import Workspace

from .models import Invitation
from .serializers import CreateInvitationSerializer, InvitationSerializer
from .services import accept_invitation, cancel_pending_invitation, create_invitation, reject_invitation

class InvitationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        normalized_email = (request.user.email or "").strip().lower()
        queryset = Invitation.objects.filter(status=Invitation.Status.PENDING).filter(
            Q(invitee=request.user) | Q(invitee_email__iexact=normalized_email)
        )
        return Response(InvitationSerializer(queryset, many=True).data)


class WorkspaceInviteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        serializer = CreateInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        channel = None
        channel_id = serializer.validated_data.get("channel_id")
        if channel_id:
            channel = get_object_or_404(Channel, pk=channel_id, workspace=workspace)

        try:
            invitation = create_invitation(
                inviter=request.user,
                workspace=workspace,
                invitee_email=serializer.validated_data["invitee_email"],
                channel=channel,
            )
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except IntegrityError:
            return Response({"detail": "Pending invitation already exists"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(InvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)


class InvitationAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, invitation_id):
        invitation = get_object_or_404(Invitation, pk=invitation_id)
        try:
            accept_invitation(invitation=invitation, user=request.user)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvitationRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, invitation_id):
        invitation = get_object_or_404(Invitation, pk=invitation_id)
        try:
            reject_invitation(invitation=invitation, user=request.user)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvitationCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, invitation_id):
        invitation = get_object_or_404(Invitation, pk=invitation_id)
        try:
            cancel_pending_invitation(invitation=invitation, actor=request.user)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
