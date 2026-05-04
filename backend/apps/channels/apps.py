from django.apps import AppConfig


class ChannelsConfig(AppConfig):
    """Label must differ from the third-party ``channels`` (Django Channels) app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.channels"
    label = "slack_channels"
