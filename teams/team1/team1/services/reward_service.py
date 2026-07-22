from ..models import ParticipantChallenge
from ..models import Reward
from ..models import UserBadge


def distribute_rewards(challenge_id):
    """
    Awards badges according to final rankings.

    Top 1  -> Top1 badge
    Top 3  -> Top3 badge
    Top 10 -> Top10 badge
    """

    participants = (
        ParticipantChallenge.objects
        .filter(
            challenge_id=challenge_id,
            final_rank__isnull=False,
        )
        .order_by("final_rank")
    )

    reward_map = {
        Reward.BadgeType.TOP_1:
            Reward.objects.get(badge_type=Reward.BadgeType.TOP_1),

        Reward.BadgeType.TOP_3:
            Reward.objects.get(badge_type=Reward.BadgeType.TOP_3),

        Reward.BadgeType.TOP_10:
            Reward.objects.get(badge_type=Reward.BadgeType.TOP_10),
    }

    for participant in participants:

        if participant.final_rank == 1:
            UserBadge.objects.get_or_create(
                user_id=participant.user_id,
                challenge=participant.challenge,
                reward=reward_map[Reward.BadgeType.TOP_1],
            )

        if participant.final_rank <= 3:
            UserBadge.objects.get_or_create(
                user_id=participant.user_id,
                challenge=participant.challenge,
                reward=reward_map[Reward.BadgeType.TOP_3],
            )

        if participant.final_rank <= 10:
            UserBadge.objects.get_or_create(
                user_id=participant.user_id,
                challenge=participant.challenge,
                reward=reward_map[Reward.BadgeType.TOP_10],
            )