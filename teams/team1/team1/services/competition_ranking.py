"""
SCRUM-28 (subtask 3): service logic to recalculate competition rankings.

Called immediately after any CompetitionParticipant.total_score update so
the `rank` field is always in sync (dense ranking: tied scores share the
same rank, and the next distinct score continues at its true position).
"""

from ..models import CompetitionParticipant


def recalculate_competition_rankings(competition_id):
    """
    Recalculates and persists `rank` for every participant of the given
    competition, ordered by total_score (highest first).

    Returns the list of participants in their new rank order.
    """
    participants = list(
        CompetitionParticipant.objects.filter(
            competition_id=competition_id
        ).order_by("-total_score", "joined_at")
    )

    current_rank = 0
    previous_score = None
    to_update = []

    for index, participant in enumerate(participants, start=1):
        if participant.total_score != previous_score:
            current_rank = index
            previous_score = participant.total_score

        if participant.rank != current_rank:
            participant.rank = current_rank
            to_update.append(participant)

    if to_update:
        CompetitionParticipant.objects.bulk_update(to_update, ["rank"])

    return participants