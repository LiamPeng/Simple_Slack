from backend.apps.channels.models import ChannelMembership
from backend.apps.workspaces.models import WorkspaceMembership


def is_workspace_member(user, workspace):
    return WorkspaceMembership.objects.filter(user=user, workspace=workspace).exists()


def is_workspace_admin(user, workspace):
    return WorkspaceMembership.objects.filter(
        user=user, workspace=workspace, role=WorkspaceMembership.Role.ADMIN
    ).exists()


def can_access_channel(user, channel):
    if channel.channel_type == channel.ChannelType.PUBLIC:
        return is_workspace_member(user, channel.workspace)
    return ChannelMembership.objects.filter(user=user, channel=channel).exists()
