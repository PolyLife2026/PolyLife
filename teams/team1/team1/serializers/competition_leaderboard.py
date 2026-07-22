from rest_framework import serializers

from ..models import CompetitionParticipant


class CompetitionLeaderboardSerializer(serializers.ModelSerializer):
    """SCRUM-29 (subtask 2): ordered leaderboard entry for a competition."""

    class Meta:
        model = CompetitionParticipant
        fields = ["user_id", "total_score", "rank", "joined_at"]