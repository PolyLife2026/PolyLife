from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


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

class Challenge(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ENDED = "ended", "Ended"
        CANCELLED = "cancelled", "Cancelled"

    class ActivityType(models.TextChoices):
        RUNNING = "running", "Running"
        SWIMMING = "swimming", "Swimming"
        CYCLING = "cycling", "Cycling"
        WALKING = "walking", "Walking"
        # add whatever set your team agrees on

    class GoalUnit(models.TextChoices):
        KM = "km", "Kilometers"
        MINUTE = "minute", "Minutes"
        STEP = "step", "Steps"
        CALORIE = "calorie", "Calories"
        KG = "kg", "Kilograms"

    challenge_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, blank=True, null=True)
    activity_type = models.CharField(max_length=50, choices=ActivityType.choices, db_index=True)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.MEDIUM, db_index=True)
    value_goal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    goal_unit = models.CharField(max_length=20, choices=GoalUnit.choices)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    created_by = models.BigIntegerField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'challenge'
        ordering = ["-created_at"]

    def clean(self):
        if self.date_start and self.date_end and self.date_end <= self.date_start:
            raise ValidationError("date_end must be after date_start.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title