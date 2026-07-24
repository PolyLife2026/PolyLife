"""
Models for managing user badges in the PolyLife project.

This module defines the UserBadge model, which links a user (from the Core 
microservice) to a specific reward/badge earned in a particular challenge.
"""

from django.db import models

from .challenge import Challenge
from .reward import Reward


class UserBadge(models.Model):
    """
    Represents a badge or reward granted to a user for a specific challenge.

    This model acts as a bridge between the Core service's users (via user_id),
    the Challenge they participated in, and the Reward (badge) they achieved.
    
    Attributes:
        user_id (BigIntegerField): The unique identifier of the user in the Core microservice. Indexed for fast lookups.
        challenge (ForeignKey): A reference to the Challenge where the badge was earned.
        reward (ForeignKey): A reference to the specific Reward (e.g., Top 1, Top 3) granted.
        issued_at (DateTimeField): The timestamp when the badge was automatically awarded.
    """

    user_id = models.BigIntegerField(db_index=True)

    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name="user_badges",
    )

    reward = models.ForeignKey(
        Reward,
        on_delete=models.CASCADE,
        related_name="awards",
    )

    issued_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        """
        Metadata for the UserBadge model.
        
        Ensures that a user cannot be awarded the exact same reward type 
        for the same challenge more than once using a UniqueConstraint.
        """
        db_table = "user_badge"
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "challenge", "reward"],
                name="unique_user_badge",
            )
        ]

    def __str__(self):
        """Returns the string representation of the granted user badge."""
        return f"{self.user_id} - {self.reward.badge_type}"
