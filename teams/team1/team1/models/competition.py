"""
Models for the Competition module in the PolyLife project.

This module defines the Competition and CompetitionParticipant models.
Since user management is handled by the Core microservice, user relations
are maintained using `user_id` (BigIntegerField) instead of ForeignKeys.
Supports soft deletion for competitions.
"""

from django.db import models
from django.core.exceptions import ValidationError


class Competition(models.Model):
    """
    Represents a fitness or health competition in the PolyLife system.

    Competitions have a defined type, status, and duration.
    They are created by a user (persisted as `created_by` from Core service)
    and support soft deletion.

    Attributes:
        competition_id (AutoField): Primary key.
        title (CharField): The title of the competition.
        description (TextField): Optional details about the competition.
        rules (TextField): Optional rules or guidelines for the competition.
        competition_type (CharField): The type of competition (e.g., weight loss, activity).
        date_start (DateTimeField): The start date and time.
        date_end (DateTimeField): The end date and time.
        status (CharField): Current status (PENDING, ACTIVE, FINISHED).
        created_by (BigIntegerField): The ID of the user who created this competition.
        created_at (DateTimeField): Auto-generated creation timestamp.
        updated_at (DateTimeField): Auto-generated update timestamp.
        is_deleted (BooleanField): Flag indicating if the competition is soft-deleted.
    """

    class CompetitionType(models.TextChoices):
        WEIGHT_LOSS = "weight_loss", "Weight loss"
        ACTIVITY_BASED = "activity_based", "Activity based"
        RECORD_BASED = "record_based", "Record based"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        FINISHED = "finished", "Finished"

    competition_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, blank=True, null=True)
    rules = models.TextField(max_length=2000, blank=True, null=True)

    competition_type = models.CharField(
        max_length=30,
        choices=CompetitionType.choices,
        db_index=True,
        help_text="The category/type of the competition."
    )

    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="Current lifecycle state of the competition."
    )

    created_by = models.BigIntegerField(
        db_index=True,
        help_text="User ID from Core service."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "competition"
        ordering = ["-created_at"]
        app_label = "team1"

    def clean(self):
        """
        Validates model fields.
        Ensures that the competition's end date is strictly after its start date.
        """
        if self.date_start and self.date_end and self.date_end <= self.date_start:
            raise ValidationError("date_end must be after date_start.")

    def __str__(self):
        """Returns the string representation of the Competition."""
        return self.title


class CompetitionParticipant(models.Model):
    """
    Represents a user's participation in a specific Competition.

    Tracks the participant's total score and current rank within the competition.
    Enforces a unique constraint so a user can join a specific competition only once.

    Attributes:
        participant_id (AutoField): Primary key.
        competition (ForeignKey): The competition the user has joined.
        user_id (BigIntegerField): ID of the participating user from the Core service.
        joined_at (DateTimeField): Auto-generated timestamp when the user joined.
        total_score (DecimalField): The accumulated score of the user in this competition.
        rank (PositiveIntegerField): The computed rank of the user based on total_score.
    """

    participant_id = models.AutoField(primary_key=True)

    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="participants",
        help_text="The competition this participant belongs to."
    )

    # User table belongs to Core service
    user_id = models.BigIntegerField(
        db_index=True,
        help_text="Participating User ID from Core service."
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    # SCRUM-28 (subtask 1): result/score fields used to compute rankings.
    total_score = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Accumulated score used for leaderboard ranking."
    )
    
    rank = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Computed leaderboard rank."
    )

    class Meta:
        db_table = "competition_participant"
        ordering = ["-joined_at"]
        app_label = "team1"
        constraints = [
            models.UniqueConstraint(
                fields=["competition", "user_id"],
                name="unique_competition_user"
            )
        ]

    def __str__(self):
        """Returns a string representation of the participant and their competition."""
        return f"{self.user_id} -> {self.competition.title}"
