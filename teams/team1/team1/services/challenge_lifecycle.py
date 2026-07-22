from django.utils import timezone

from ..models import Challenge
from .final_ranking import calculate_final_rankings


def refresh_challenge_status(challenge):
    """
    Transition challenge status based on current time:
    created -> started when date_start is reached
    started/created -> ended when date_end is reached
    """
    if challenge.is_deleted or challenge.status == Challenge.Status.CANCELLED:
        return challenge

    now = timezone.now()

    if challenge.date_end <= now:
        if challenge.status != Challenge.Status.ENDED:
            challenge.status = Challenge.Status.ENDED
            challenge.save(update_fields=["status"])
            calculate_final_rankings(challenge.challenge_id)
        return challenge

    if (
        challenge.status == Challenge.Status.CREATED
        and challenge.date_start <= now
    ):
        challenge.status = Challenge.Status.STARTED
        challenge.save(update_fields=["status"])

    return challenge


def refresh_all_challenge_statuses():
    """Refresh statuses for all non-cancelled, non-deleted challenges."""
    challenges = Challenge.objects.filter(is_deleted=False).exclude(
        status=Challenge.Status.CANCELLED
    )
    for challenge in challenges:
        refresh_challenge_status(challenge)
