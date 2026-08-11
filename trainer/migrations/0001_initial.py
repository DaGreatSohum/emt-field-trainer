from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="TrainingAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scenario_key", models.CharField(db_index=True, max_length=100)),
                ("score", models.PositiveSmallIntegerField(default=0)),
                ("completed", models.BooleanField(default=False)),
                ("current_step", models.PositiveSmallIntegerField(default=0)),
                ("transcript", models.JSONField(default=list)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-updated_at"]},
        )
    ]
