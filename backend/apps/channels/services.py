from django.db import transaction

from .models import Channel, ChannelMembership


@transaction.atomic
def create_channel_with_creator(*, workspace, creator, name, channel_type):
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
    channel = Channel.objects.create(
        workspace=workspace,
        creator=creator,
        name=f"dm-{min(creator.id, other_user.id)}-{max(creator.id, other_user.id)}",
        channel_type=Channel.ChannelType.DIRECT,
    )
    ChannelMembership.objects.create(channel=channel, user=creator)
    ChannelMembership.objects.create(channel=channel, user=other_user)
    return channel
