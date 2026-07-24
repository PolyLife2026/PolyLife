"""
Models for managing participant scores in PolyLife challenges.

This module defines the ParticipantScore model, which tracks the exact score 
achieved by a user within a specific challenge.
"""

from django.db import models
from .challenge import Challenge


class ParticipantScore(models.Model):
    """
    Represents the score of a participant in a specific challenge.

    This model links a user (via Core microservice `user_id`) to a `Challenge` 
    and records their current score. It includes constraints to ensure a user 
    has only one score record per challenge and provides an optimized index 
    for fast leaderboard generation (sorting by score descending).

    Attributes:
        score_id (AutoField): The primary key for the score record.
        challenge (ForeignKey): The challenge associated with this score.
        user_id (BigIntegerField): The ID of the user from the Core microservice.
        score (DecimalField): The user's score in the challenge (max 999999.99).
        updated_at (DateTimeField): Auto-generated timestamp of the last score update.
    """
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
        """
        Metadata for the ParticipantScore model.

        Enforces uniqueness for (challenge, user_id) to prevent duplicate scores,
        and sets up a composite index to optimize descending leaderboard queries.
        """
        db_table = "participant_score"
        unique_together = ("challenge", "user_id")
        indexes = [
            models.Index(fields=["challenge", "-score"], name="idx_score_challenge"),
        ]

    def __str__(self):
        """Returns a string representation of the participant's score."""
        return f"{self.user_id} - {self.challenge_id} - {self.score}"
