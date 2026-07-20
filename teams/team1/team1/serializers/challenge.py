from rest_framework import serializers
from .models import Challenge

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'  
        
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
