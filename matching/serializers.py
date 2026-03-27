from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import(
    MatchPreference, SkillMatch, MatchSuggestion, 
    SavedMatch, MatchFilter, MatchAnalytics, MatchFeedback
)

User = get_user_model()

class MatchPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for match preferences"""
    class Meta:
        model = MatchPreference
        fields = [
            'id','user','max_distance','meeting_preference'
            ,'available_weekdays','available_afternoons','prefer_verified_users'
            ,'created_at','updated_at'
        ]
        
        read_only_fields = ['id','user','created_at','updated_at']
        
        
    def create(self, validated_data):
            validated_data['user']= self.context['request'].user
            return super().create(validated_data)
        
        
        
        