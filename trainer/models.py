import uuid

from django.db import models


class TrainingAttempt(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    access_token_hash = models.CharField(max_length=64, editable=False)
    scenario_key = models.CharField(max_length=100, db_index=True)
    score = models.PositiveSmallIntegerField(default=0)
    completed = models.BooleanField(default=False)
    current_step = models.PositiveSmallIntegerField(default=0)
    transcript = models.JSONField(default=list)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.scenario_key} - {self.score}%"
