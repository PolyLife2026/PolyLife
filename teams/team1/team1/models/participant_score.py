from django.db import models
from .challenge import Challenge


class ParticipantScore(models.Model):
    score_id = models.AutoField(primary_key=True)

    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name="participant_scores",
    )

    user_id = models.BigIntegerField(db_index=True)

    score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "participant_score"
        unique_together = ("challenge", "user_id")

    def __str__(self):
        return f"{self.user_id} - {self.challenge_id} - {self.score}"