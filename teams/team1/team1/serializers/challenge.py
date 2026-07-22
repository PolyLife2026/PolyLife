from rest_framework import serializers
from ..models import Challenge, ParticipantChallenge
from decimal import Decimal
from django.core.validators import MinValueValidator
from ..models import UserBadge, Reward

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
    

class ChallengeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving challenge details (Public fields only).
    Excluded internal fields like is_deleted, created_at, updated_at.
    """
    is_joined = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        
        fields = [
            'challenge_id', 
            'title', 
            'description', 
            'activity_type', 
            'difficulty', 
            'value_goal', 
            'goal_unit', 
            'date_start', 
            'date_end', 
            'status', 
            'created_by',
            'is_joined',
        ]
        
        # Ensure it's read-only since this is for a GET request
        read_only_fields = fields

    def get_is_joined(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user_id = request.META.get('HTTP_X_USER_ID')
        if not user_id:
            return False
        return ParticipantChallenge.objects.filter(
            challenge=obj,
            user_id=int(user_id),
        ).exists()

    # def get_participant_count(self, obj):
    #     # NOTE: If you set a 'related_name' in your Participant model's 
    #     # ForeignKey (e.g., related_name='participants'), change 'participant_set' 
    #     # to that related_name (e.g., obj.participants.filter(...)).
        
    #     # Filter out soft-deleted participants to get the true active count
    #     return obj.participant_set.filter(is_deleted=False).count()


class ChallengeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        # Exclude internal fields; only expose public info for the list
        fields = [
            'challenge_id', 
            'title', 
            'status', 
            'date_start', 
            'date_end'
        ]


class LeaderboardSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    user_id = serializers.IntegerField()
    score = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

class ChallengeResultSerializer(serializers.Serializer):
    final_rank = serializers.IntegerField()

    total_score = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    badges = serializers.ListField(
        child=serializers.CharField()
    )

    rewards = serializers.ListField(
        child=serializers.CharField()
    )