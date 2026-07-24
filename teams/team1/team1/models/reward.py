"""
Models for managing rewards and badges in the PolyLife project.

This module defines the Reward model, which represents the different types 
of badges (e.g., Top 1, Top 3) that can be awarded to users based on their 
performance in challenges or competitions.
"""

from django.db import models


class Reward(models.Model):
    """
    Represents a reward or badge achievable by participants.

    This model stores the predefined badge types and their descriptions. 
    It is used to grant specific recognitions to users upon completing 
    challenges or competitions with high ranks.

    Attributes:
        badge_type (CharField): The unique identifier and type of the badge (e.g., 'top1').
        description (CharField): A brief, optional description of the reward.
        created_at (DateTimeField): Auto-generated timestamp of when the reward was created.
    """

    class BadgeType(models.TextChoices):
        """
        Enumeration for the available types of badges.
        """
        TOP_1 = "top1", "Top 1"
        TOP_3 = "top3", "Top 3"
        TOP_10 = "top10", "Top 10"

    badge_type = models.CharField(
        max_length=20,
        choices=BadgeType.choices,
        unique=True,
    )

    description = models.CharField(
        max_length=100,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Metadata for the Reward model.
        """
        db_table = "reward"

    def __str__(self):
        """Returns the string representation of the reward."""
        return str(self.badge_type)
