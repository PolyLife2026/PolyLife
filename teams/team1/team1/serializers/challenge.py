from rest_framework import serializers
from ..models import Challenge
from decimal import Decimal
from django.core.validators import MinValueValidator

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'
        read_only_fields = (
            'challenge_id',
            'created_at',
            'updated_at',
            'is_deleted',
            'created_by',
        )
        
    def validate(self, data):
        if data.get('date_start') and data.get('date_end'):
            if data['date_end'] <= data['date_start']:
                raise serializers.ValidationError({
                    "date_end": "the end date (date_end) must be after the start date (date_start)."
                })
        
        if data.get('value_goal') and data['value_goal'] <= 0:
            raise serializers.ValidationError({
                "value_goal": "the value goal (value_goal) must be a positive number."
            })
            
        return data


class LeaderboardSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    user_id = serializers.IntegerField()
    score = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
    )