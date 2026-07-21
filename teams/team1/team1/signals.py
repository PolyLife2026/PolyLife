from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum

from .models import Activity, ParticipantScore


@receiver(post_save, sender=Activity)
def update_participant_score(sender, instance, **kwargs):

    total = (
            Activity.objects.filter(
                challenge=instance.challenge,
                user_id=instance.user_id,
                is_deleted=False,
            ).aggregate(total=Sum("value"))["total"]
            or Decimal("0")
    )

    score = round(
        (total / instance.challenge.value_goal) * Decimal("100"),
        2,
        )

    ParticipantScore.objects.update_or_create(
        challenge=instance.challenge,
        user_id=instance.user_id,
        defaults={
            "score": score
        }
    )