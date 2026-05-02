# Generated manually — align Message with sql/01_schema.sql (body, no updated_at)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat_messages", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="message",
            old_name="content",
            new_name="body",
        ),
        migrations.RemoveField(
            model_name="message",
            name="updated_at",
        ),
    ]
