# Generated manually — index for chronological listing per channel

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat_messages", "0002_message_schema_alignment"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="message",
            index=models.Index(fields=["channel", "created_at"], name="chat_messages_channel_created_idx"),
        ),
    ]
