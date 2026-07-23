from django.db import models
from django.utils import timezone


class Competition(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("started", "Started"),
        ("finished", "Finished"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending"
    )
    created_by = models.IntegerField(db_index=True)  # coach user_id
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def update_status(self):
        """
        Automatically transition competition status based on current time.
        Called before any query to ensure status is accurate.
        Transitions: pending -> started -> finished
        """
        now = timezone.now()
        
        if now >= self.end_date and self.status != "finished":
            self.status = "finished"
            self.save()
        elif now >= self.start_date and self.status == "pending":
            self.status = "started"
            self.save()


class Activity(models.Model):
    ACTIVITY_TYPES = [
        ("run", "Running"),
        ("walk", "Walking"),
        ("swim", "Swimming"),
        ("cycle", "Cycling"),
        ("gym", "Gym"),
        ("sports", "Sports"),
        ("other", "Other"),
    ]

    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, related_name="activities"
    )
    user_id = models.IntegerField(db_index=True)  # participant user_id
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    distance = models.FloatField(null=True, blank=True, help_text="Distance in km")
    duration = models.IntegerField(
        null=True, blank=True, help_text="Duration in minutes"
    )
    calories_burned = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    activity_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-activity_date"]
        indexes = [
            models.Index(fields=["competition", "user_id"]),
            models.Index(fields=["competition", "activity_date"]),
        ]

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.user_id}"


class Leaderboard(models.Model):
    """
    Denormalized leaderboard for fast queries.
    Updated whenever an activity is added/modified.
    """

    competition = models.OneToOneField(
        Competition, on_delete=models.CASCADE, related_name="leaderboard"
    )
    user_id = models.IntegerField(db_index=True)
    username = models.CharField(max_length=150, blank=True)
    total_activities = models.IntegerField(default=0)
    total_distance = models.FloatField(default=0)
    total_duration = models.IntegerField(default=0)  # in minutes
    total_calories = models.IntegerField(default=0)
    last_activity_date = models.DateTimeField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("competition", "user_id")
        ordering = ["-total_distance", "-total_activities"]

    def __str__(self):
        return f"{self.username} - {self.competition.title}"

    def calculate_score(self):
        """
        Calculate a composite score for ranking.
        Can be customized based on your needs.
        """
        return (
            self.total_distance * 10 + self.total_activities * 5 + self.total_calories / 100
        )
