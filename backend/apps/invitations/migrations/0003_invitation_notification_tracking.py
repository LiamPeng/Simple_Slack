from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invitations", "0002_workspace_invitation_alignment"),
    ]

    operations = [
        migrations.AddField(
            model_name="invitation",
            name="last_notified_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="invitation",
            name="notification_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
