from django.db import models

from .challenge import Challenge
from .reward import Reward


class UserBadge(models.Model):

    user_id = models.BigIntegerField(db_index=True)

    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name="user_badges",
    )

    reward = models.ForeignKey(
        Reward,
        on_delete=models.CASCADE,
        related_name="awards",
    )

    issued_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "user_badge"
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "challenge", "reward"],
                name="unique_user_badge",
            )
        ]

    def __str__(self):
        return f"{self.user_id} - {self.reward.badge_type}"