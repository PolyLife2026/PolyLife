from django.db import transaction

from ..models import ParticipantChallenge
from ..models import ParticipantScore


@transaction.atomic
def calculate_final_rankings(challenge_id):
    """
    Permanently assigns final rankings when a challenge ends.

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

    if updates:
        ParticipantChallenge.objects.bulk_update(
            updates,
            ["final_rank"],
        )

    return updates