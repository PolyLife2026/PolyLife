from rest_framework import serializers


class CompetitionResultSerializer(serializers.Serializer):
    """
    SCRUM-28 (subtask 2): payload for recording/updating a participant's
    competition score. Not a ModelSerializer since it targets a specific
    CompetitionParticipant row (looked up by user_id) rather than creating
    a new row.
    """

    user_id = serializers.IntegerField()
    score = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_score(self, value):
        if value < 0:
            raise serializers.ValidationError("score must not be negative.")
        return value