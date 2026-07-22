from django.db import transaction

from ..models import ParticipantChallenge
from ..models import ParticipantScore
from .reward_service import distribute_rewards



@transaction.atomic
def calculate_final_rankings(challenge_id):
    """
    Permanently assigns final ranks after challenge closes.

    Tie-breaking:
        1. Higher score
        2. Smaller user_id
    """

    scores = (
        ParticipantScore.objects
        .select_for_update()
        .filter(challenge_id=challenge_id)
        .order_by("-score", "user_id")
    )

    current_rank = 1
    updates = []

    for score in scores:

        participant = (
            ParticipantChallenge.objects
            .select_for_update()
            .get(
                challenge_id=challenge_id,
                user_id=score.user_id,
            )
        )

        participant.final_rank = current_rank
        updates.append(participant)
        current_rank += 1

    ParticipantChallenge.objects.bulk_update(
        updates,
        ["final_rank"],
    )

    # Award badges
    distribute_rewards(challenge_id)

    return updates