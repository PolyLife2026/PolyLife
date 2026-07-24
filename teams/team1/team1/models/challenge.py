"""
Models for the Challenge module.

This module defines the Challenge model and its associated manager, handling
the core structure for fitness/activity challenges in the PolyLife system.
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
#from ..views.challenge_views import ChallengeCreateView


class ActiveChallengeManager(models.Manager):
    """
    Custom manager for the Challenge model.
    
    Filters out soft-deleted challenges from the default queryset, ensuring
    that only active (non-deleted) records are returned by default.
    """
    def get_queryset(self):
        # Only return challenges that are not deleted
        return super().get_queryset().filter(is_deleted=False)


class Challenge(models.Model):
    """
    Represents a physical activity challenge within the PolyLife system.

    A Challenge defines a specific fitness goal (e.g., running 10 km) over a 
    set timeframe. Users can join challenges and submit activities towards 
    completing them. Supports soft deletion via the `is_deleted` flag.
    
    Attributes:
        challenge_id (AutoField): The primary key for the challenge.
        title (CharField): The title of the challenge.
        description (TextField): Optional detailed description.
        activity_type (CharField): The type of physical activity required.
        difficulty (CharField): The difficulty level of the challenge.
        value_goal (DecimalField): The numerical target to achieve.
        goal_unit (CharField): The unit of measurement for the goal.
        date_start (DateTimeField): The start date and time of the challenge.
        date_end (DateTimeField): The end date and time of the challenge.
        status (CharField): Current lifecycle status of the challenge.
        created_by (BigIntegerField): User ID (from API Gateway) of the creator.
        created_at (DateTimeField): Auto-generated creation timestamp.
        updated_at (DateTimeField): Auto-generated update timestamp.
        is_deleted (BooleanField): Flag indicating if the record is soft-deleted.
    """

    class Difficulty(models.TextChoices):
        """Available difficulty levels for a challenge."""
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    class Status(models.TextChoices):
        """Lifecycle stages of a challenge."""
        CREATED = "created", "Created"
        STARTED = "started", "Started"
        ENDED = "ended", "Ended"
        CANCELLED = "cancelled", "Cancelled"

    class ActivityType(models.TextChoices):
        """Types of physical activities supported by challenges."""
        RUNNING = "running", "Running"
        SWIMMING = "swimming", "Swimming"
        CYCLING = "cycling", "Cycling"
        WALKING = "walking", "Walking"

    class GoalUnit(models.TextChoices):
        """Units of measurement used to track challenge goals."""
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
        """Returns the string representation of the Challenge."""
        return self.title
