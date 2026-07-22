from django.db import models

class Reward(models.Model):

    class BadgeType(models.TextChoices):
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
        db_table = "reward"

    def __str__(self):
        return self.badge_type