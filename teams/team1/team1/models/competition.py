from django.db import models
from django.core.exceptions import ValidationError


class Competition(models.Model):
    """
    SCRUM-122: Design and implement Competition model.

    A coach/admin-defined competition (e.g. weight-loss, activity-based,
    or record-based). Distinct from Challenge: a Competition tracks
    participants' recorded results (SCRUM-131) and produces a ranked
    leaderboard (SCRUM-135) and final rankings (SCRUM-139) once it ends.
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

    # Explicitly requested by SCRUM-122: free-text rules shown to
    # participants before they join (scoring rules, fair-play rules, etc).
    rules = models.TextField(max_length=2000, blank=True, null=True)

    competition_type = models.CharField(
        max_length=30, choices=CompetitionType.choices, db_index=True
    )

    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )

    # Owner of this record (coach/admin). Not a FK: the User table is owned
    # by the Core service, in a different database than this microservice's
    # (same convention as Challenge.created_by).
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