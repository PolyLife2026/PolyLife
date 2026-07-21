from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
#from ..views.challenge_views import ChallengeCreateView


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

class ActiveChallengeManager(models.Manager):
    def get_queryset(self):
        # Only return challenges that are not deleted
        return super().get_queryset().filter(is_deleted=False)

class Challenge(models.Model):

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy", "EASY"
        MEDIUM = "medium", "Medium", "MEDIUM"
        HARD = "hard", "Hard", "HARD"

    class Status(models.TextChoices):
        CREATED = "created", "Created", "CREATED"
        STARTED = "started", "Started", "STARTED"
        ENDED = "ended", "Ended", "ENDED"
        CANCELLED = "cancelled", "Cancelled", "CANCELLED"

    class ActivityType(models.TextChoices):
        RUNNING = "running", "Running", "RUNNING"
        SWIMMING = "swimming", "Swimming", "SWIMMING"
        CYCLING = "cycling", "Cycling", "CYCLING"
        WALKING = "walking", "Walking", "WALKING"

    class GoalUnit(models.TextChoices):
        KM = "km", "Kilometers", "KM", "KILOMETERS"
        MINUTE = "minute", "Minutes", "MINUTE", "MINUTES"
        STEP = "step", "Steps", "STEP", "STEPS"
        CALORIE = "calorie", "Calories", "CALORIE", "CALORIES"
        KG = "kg", "Kilograms", "KG", "KILOGRAMS"

    challenge_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, blank=True, null=True)
    activity_type = models.CharField(max_length=50, choices=ActivityType.choices, db_index=True)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.MEDIUM, db_index=True)
    value_goal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    goal_unit = models.CharField(max_length=20, choices=GoalUnit.choices)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, db_index=True)
    created_by = models.BigIntegerField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_deleted = models.BooleanField(default=False)

    # Overriding the default manager to prevent showing the deleted challenges in the queryset
    objects = ActiveChallengeManager()
    
    # Keeping a reference to the default manager to access deleted items if needed
    all_objects = models.Manager()

    class Meta:
        db_table = 'challenge'
        ordering = ["-created_at"]
        app_label = 'team1'

    def __str__(self):
        return self.title