from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invitations", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="invitation",
            table="WorkspaceInvitation",
        ),
        migrations.AddField(
            model_name="invitation",
            name="invitee_email",
            field=models.EmailField(default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="invitation",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_column="invited_at"),
        ),
        migrations.AlterField(
            model_name="invitation",
            name="invitee",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="received_invitations",
                to="accounts.appuser",
            ),
        ),
        migrations.AlterField(
            model_name="invitation",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("accepted", "Accepted"), ("declined", "Declined")],
                default="pending",
                max_length=16,
            ),
        ),
        migrations.RunSQL(
            sql="UPDATE \"WorkspaceInvitation\" SET status = 'declined' WHERE status = 'rejected';",
            reverse_sql="UPDATE \"WorkspaceInvitation\" SET status = 'rejected' WHERE status = 'declined';",
        ),
        migrations.RemoveConstraint(
            model_name="invitation",
            name="uniq_pending_invitation",
        ),
        migrations.AddConstraint(
            model_name="invitation",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "pending")),
                fields=("invitee_email", "workspace", "channel"),
                name="uniq_pending_invitation",
            ),
        ),
    ]
