from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="workspace",
            table="Workspace",
        ),
        migrations.AlterModelTable(
            name="workspacemembership",
            table="WorkspaceMembership",
        ),
    ]
