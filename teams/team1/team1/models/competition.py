from django.db import models
from django.core.exceptions import ValidationError


class Competition(models.Model):

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
        db_index=True
    )

    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    created_by = models.BigIntegerField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "competition"
        ordering = ["-created_at"]
        app_label = "team1"

    def clean(self):
        if self.date_start and self.date_end and self.date_end <= self.date_start:
            raise ValidationError("date_end must be after date_start.")

    def __str__(self):
        return self.title


class CompetitionParticipant(models.Model):

    participant_id = models.AutoField(primary_key=True)

    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="participants"
    )

    # User table belongs to Core service
    user_id = models.BigIntegerField(db_index=True)

    joined_at = models.DateTimeField(auto_now_add=True)

    # SCRUM-28 (subtask 1): result/score fields used to compute rankings.
    total_score = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    rank = models.PositiveIntegerField(null=True, blank=True)

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
        return f"{self.user_id} -> {self.competition.title}"