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
        
        
class SkillMatchSerializer(serializers.ModelSerializer):
    """Serializer for skill matches"""
    user1_name = serializers.CharField(source='user1.get_full_name',read_only= True)
    user1_email = serializers.CharField(source = 'user1.email',read_only = True)
    user1_profile_picture = serializers.ImageField(source = 'user1.profile_picture',read_only = True)
    user1_location = serializers.CharField(source = 'user1.location', read_only = True)
    user1_skill_name = serializers.CharField(source = 'user1_skill.name', read_only = True)
    user2_skill_name = serializers.SerializerMethodField()
    
    
    class Meta:
        model = SkillMatch
        fields = [
            'id', 'user1', 'user1_name', 'user1_email', 'user1_profile_picture',
            'user1_location', 'user1_rating',
            'user2', 'user2_name', 'user2_email', 'user2_profile_picture',
            'user2_location', 'user2_rating',
            'user1_skill', 'user1_skill_name', 'user2_skill', 'user2_skill_name',
            'match_type', 'match_score', 'skill_compatibility',
            'location_compatibility', 'availability_compatibility',
            'experience_compatibility', 'rating_compatibility',
            'is_active', 'viewed_by_user1', 'viewed_by_user2',
            'user1_interested', 'user2_interested', 'exchange_request_created',
            'created_at', 'updated_at'
        ]
        
        read_only_fields = ['id','created_at','updated_at']
        
        def get_user1_rating(self,obj):
            ratings = obj.user1.ratings_received.all()
            if ratings.exists():
                return round(sum(r.ratings for r in ratings)/ ratings.count(),2)
            return None
        
        def get_user2_rating(self, obj):
            ratings = obj.user2.ratings_received.all()
            if ratings.exists():
                return round(sum(r.rating for r in ratings)/ ratings.count(),2)
            return None