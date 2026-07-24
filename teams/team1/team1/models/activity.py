"""
Models for the Activity module.

This module defines the Activity model, which represents a single activity
submission made by a participant (user) against a specific fitness challenge.
User management belongs to the Core service, so this model only persists the
user_id received from the API Gateway via the X-User-Id header.
"""

from django.db import models
from django.core.validators import MinValueValidator
from .challenge import Challenge  # adjust import path if your app layout differs


class Activity(models.Model):
    """
    Represents one daily activity record submitted by a participant for a challenge.
    
    The submitted `value` contributes toward the parent Challenge's `value_goal`, 
    expressed in the same `goal_unit`. Supports soft deletion via the `is_deleted` flag.

    Attributes:
        activity_id (AutoField): The primary key for the activity record.
        user_id (BigIntegerField): ID of the participant, taken from the X-User-Id header.
        challenge (ForeignKey): The Challenge this activity contributes progress to.
        value (DecimalField): Positive numeric value representing the recorded progress.
        activity_date (DateField): The actual date the activity took place.
        note (CharField): Optional free-text note from the participant.
        created_at (DateTimeField): Auto-generated creation timestamp.
        updated_at (DateTimeField): Auto-generated update timestamp.
        is_deleted (BooleanField): Flag indicating if the record is soft-deleted.
    """

    activity_id = models.AutoField(primary_key=True)

    user_id = models.BigIntegerField(
        db_index=True,
        help_text="ID of the participant, taken from the X-User-Id header.",
    )

    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name="activities",
        db_index=True,
        help_text="Challenge this activity contributes progress to.",
    )

    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Positive numeric value representing the recorded progress.",
    )

    activity_date = models.DateField(
        db_index=True,
        help_text="The date the activity actually took place.",
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional free-text note from the participant.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "activity"
        indexes = [
            models.Index(fields=["user_id", "challenge"], name="idx_activity_user_challenge"),
            models.Index(fields=["challenge", "activity_date"], name="idx_activity_challenge_date"),
        ]
        ordering = ["-activity_date", "-created_at"]

    def __str__(self):
        """Returns the string representation of the Activity."""
        return f"Activity(user={self.user_id}, challenge={self.challenge_id}, value={self.value})"
