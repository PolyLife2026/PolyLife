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
    

class ChallengeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving challenge details (Public fields only).
    Excluded internal fields like is_deleted, created_at, updated_at.
    """
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
            'created_by' 
        ]
        
        # Ensure it's read-only since this is for a GET request
        read_only_fields = fields


