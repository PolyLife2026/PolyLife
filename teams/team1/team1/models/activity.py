
from django.db import models
from django.core.validators import MinValueValidator
from .challenge import Challenge  # adjust import path if your app layout differs

# Your team's data models go here. They live in YOUR database (the core's
# router routes "team1" models to the "team1" database automatically).
#
# Link rows to the logged-in user by their core id — store the id, do NOT add a
# ForeignKey to the core User (it lives in a different database).
#
# Example (uncomment and adapt):
#
# class Note(models.Model):
#     user_id = models.IntegerField(db_index=True)   # comes from X-User-Id
#     text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

"""
SCRUM-84: Design and implement Activity model.

Represents a single activity submission made by a participant (user)
against a specific challenge. The user itself is NOT stored as a local
FK because user management belongs to the Core service; we only persist
the user_id we receive from the Gateway via the X-User-Id header.
"""



class Activity(models.Model):
    """
    One daily activity record submitted by a participant for a challenge.
    The submitted `value` contributes toward the parent Challenge's
    `value_goal`, expressed in the same `goal_unit`.
    """

    # Explicit PK name, matching the team's convention used in Challenge
    # (challenge_id) rather than Django's default "id".
    activity_id = models.AutoField(primary_key=True)

    # Owner of this activity record. Not a FK: the User table is owned by
    # the Core service, in a different database than this microservice's.
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

    # The measured progress value for this submission, in the same unit as
    # challenge.goal_unit (km, minute, step, calorie, kg). Uses Decimal to
    # match Challenge.value_goal and avoid float rounding drift when values
    # are later summed for progress/leaderboards.
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Positive numeric value representing the recorded progress.",
    )

    # The calendar date this activity refers to (not the submission time).
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

    # --- Mandatory bookkeeping columns required by the project spec ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "activity"
        indexes = [
            # Speeds up "give me all activities for this user in this challenge"
            models.Index(fields=["user_id", "challenge"], name="idx_activity_user_challenge"),
            # Speeds up per-day lookups / leaderboard style aggregations
            models.Index(fields=["challenge", "activity_date"], name="idx_activity_challenge_date"),
        ]
        ordering = ["-activity_date", "-created_at"]

    def __str__(self):
        return f"Activity(user={self.user_id}, challenge={self.challenge_id}, value={self.value})"