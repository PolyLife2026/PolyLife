from rest_framework import serializers

from ..models import Activity, Challenge


class ActivitySerializer(serializers.ModelSerializer):
    # user_id is never taken from client input — the view sets it from the
    # X-User-Id header (see SCRUM-86), so we expose it as read-only here.
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Activity
        fields = '__all__'
        read_only_fields = ('activity_id', 'user_id', 'created_at', 'updated_at', 'is_deleted')

    def validate(self, data):
        # --- positive value check ---
        # (MinValueValidator already guards this at the model level, but we
        # re-check here so the client gets a clear, immediate error message.)
        if data.get('value') is not None and data['value'] <= 0:
            raise serializers.ValidationError({
                "value": "the activity value must be a positive number."
            })

        # --- valid challenge check ---
        challenge = data.get('challenge')
        if challenge is None:
            raise serializers.ValidationError({
                "challenge": "a valid challenge must be specified."
            })

        if challenge.is_deleted:
            raise serializers.ValidationError({
                "challenge": "this challenge no longer exists."
            })

        if challenge.status != Challenge.Status.ACTIVE:
            raise serializers.ValidationError({
                "challenge": "activities can only be submitted to an active challenge."
            })

        # Note: checking that activity_date falls within
        # challenge.date_start / challenge.date_end is handled separately
        # in SCRUM-87 (validate the challenge's active date window).

        return data