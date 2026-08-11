import hashlib
import secrets
import uuid

from django.db import migrations, models


def secure_existing_attempts(apps, schema_editor):
    Attempt = apps.get_model("trainer", "TrainingAttempt")
    for attempt in Attempt.objects.all().iterator():
        attempt.public_id = uuid.uuid4()
        attempt.access_token_hash = hashlib.sha256(
            secrets.token_bytes(32)
        ).hexdigest()
        attempt.save(update_fields=["public_id", "access_token_hash"])


class Migration(migrations.Migration):
    dependencies = [("trainer", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="trainingattempt",
            name="access_token_hash",
            field=models.CharField(default="", editable=False, max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="trainingattempt",
            name="public_id",
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.RunPython(secure_existing_attempts, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="trainingattempt",
            name="public_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
