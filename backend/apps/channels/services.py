from django.db import transaction

from backend.apps.workspaces.models import WorkspaceMembership

from .models import Channel, ChannelMembership


def _is_workspace_member(*, workspace, user):
    return WorkspaceMembership.objects.filter(workspace=workspace, user=user).exists()


@transaction.atomic
def create_channel_with_creator(*, workspace, creator, name, channel_type):
    if channel_type == Channel.ChannelType.DIRECT:
        raise ValueError("Use create_direct_channel to create direct channels")
    if not _is_workspace_member(workspace=workspace, user=creator):
        raise PermissionError("Creator must be a workspace member")

    channel = Channel.objects.create(
        workspace=workspace,
        creator=creator,
        name=name,
        channel_type=channel_type,
    )
    ChannelMembership.objects.create(channel=channel, user=creator)
    return channel


@transaction.atomic
def create_direct_channel(*, workspace, creator, other_user):
    if creator.pk == other_user.pk:
        raise ValueError("Direct channels require two different users")
    if not _is_workspace_member(workspace=workspace, user=creator):
        raise PermissionError("Creator must be a workspace member")
    if not _is_workspace_member(workspace=workspace, user=other_user):
        raise ValueError("User must be a workspace member before joining a channel")

    channel_name = f"dm-{min(creator.id, other_user.id)}-{max(creator.id, other_user.id)}"
    if Channel.objects.filter(workspace=workspace, name=channel_name).exists():
        raise ValueError("Direct channel already exists")

    channel = Channel.objects.create(
        workspace=workspace,
        creator=creator,
        name=channel_name,
        channel_type=Channel.ChannelType.DIRECT,
    )
    ChannelMembership.objects.create(channel=channel, user=creator)
    ChannelMembership.objects.create(channel=channel, user=other_user)
    return channel


@transaction.atomic
def get_or_create_direct_channel(*, workspace, creator, other_user):
    if creator.pk == other_user.pk:
        raise ValueError("Direct channels require two different users")
    if not _is_workspace_member(workspace=workspace, user=creator):
        raise PermissionError("Creator must be a workspace member")
    if not _is_workspace_member(workspace=workspace, user=other_user):
        raise ValueError("User must be a workspace member before joining a channel")

    channel_name = f"dm-{min(creator.id, other_user.id)}-{max(creator.id, other_user.id)}"
    channel = Channel.objects.filter(
        workspace=workspace,
        name=channel_name,
        channel_type=Channel.ChannelType.DIRECT,
    ).first()
    if channel:
        return channel

    return create_direct_channel(workspace=workspace, creator=creator, other_user=other_user)
