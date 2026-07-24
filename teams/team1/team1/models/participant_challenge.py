"""
Models for tracking user participation in challenges within the PolyLife project.

This module defines the ParticipantChallenge model which links users
(from the Core microservice) to specific challenges, tracking their progress,
scores, and rankings.
"""

from django.db import models
from ..models import Challenge


class ParticipantChallenge(models.Model):
    """
    Represents a user's participation and progress in a specific Challenge.

    This model tracks the current progress, total score, and both live and final
    rankings of a user within a challenge. User relations are maintained using 
    `user_id` instead of a foreign key, as user data resides in the Core microservice.
    It enforces a unique constraint preventing a user from joining the same challenge
    multiple times and supports soft deletion.

    Attributes:
        challenge (ForeignKey): The associated Challenge the user has joined.
        user_id (IntegerField): ID of the participating user from the Core service.
        joined_at (DateTimeField): Auto-generated timestamp when the user joined.
        progress_current (PositiveIntegerField): The user's current progress value.
        score_total (IntegerField): The total score accumulated by the user in this challenge.
        rank (PositiveIntegerField): The live, dynamically updated rank (optional).
        final_rank (PositiveIntegerField): The permanent rank assigned after the challenge ends (optional).
        created_at (DateTimeField): Auto-generated creation timestamp.
        updated_at (DateTimeField): Auto-generated update timestamp.
        is_deleted (BooleanField): Flag indicating if the participation record is soft-deleted.
    """
    
    challenge = models.ForeignKey(
        "Challenge",
        on_delete=models.CASCADE,
        related_name="participants"
    )

    user_id = models.IntegerField(db_index=True)

    joined_at = models.DateTimeField(auto_now_add=True)
    progress_current = models.PositiveIntegerField(default=0)
    score_total = models.IntegerField(default=0)

    # Live rank (optional)
    rank = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    # Permanent rank after challenge ends
    final_rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "participant_challenge"
        constraints = [
            models.UniqueConstraint(
                fields=["challenge", "user_id"],
                name="unique_challenge_user",
            )
        ]

    def __str__(self):
        """Returns a string representation of the user's challenge participation."""
        return f"User {self.user_id} - Challenge {self.challenge_id}"
