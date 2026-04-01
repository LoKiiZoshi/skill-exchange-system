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
        
class MatchSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for match suggestions"""
    suggested_user_name = serializers.CharField(source='suggested_user.get_full_name', read_only=True)
    suggested_user_email = serializers.CharField(source='suggested_user.email', read_only=True)
    suggested_user_profile = serializers.ImageField(source='suggested_user.profile_picture', read_only=True)
    suggested_user_location = serializers.CharField(source='suggested_user.location', read_only=True)
    suggested_user_bio = serializers.CharField(source='suggested_user.bio', read_only=True)
    
    primary_skill_name = serializers.CharField(source='primary_skill.name', read_only=True)
    secondary_skill_name = serializers.CharField(source='secondary_skill.name', read_only=True)
    
    suggested_user_rating = serializers.SerializerMethodField()
 
    class Meta:
        model = MatchSuggestion
        fields = [
            'id', 'user', 'suggested_user', 'suggested_user_name',
            'suggested_user_email', 'suggested_user_profile',
            'suggested_user_location', 'suggested_user_bio',
            'suggested_user_rating', 'suggestion_type', 'reason',
            'primary_skill', 'primary_skill_name', 'secondary_skill',
            'secondary_skill_name', 'suggestion_score', 'viewed',
            'viewed_at', 'dismissed', 'dismissed_at', 'accepted',
            'accepted_at', 'created_at', 'expires_at'
        ]
        read_only_fields = [
            'id', 'user', 'viewed_at', 'dismissed_at', 'accepted_at', 'created_at'
        ]
 
    def get_suggested_user_rating(self, obj):
        ratings = obj.suggested_user.ratings_received.all()
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 2)
        return None
 
class SaveMatchSerializers(serializers.ModelSerializer):
    """Serializer for saved matches"""
    matched_user_name = serializers.CharField(source = 'matched_user.get_full_name',read_only = True)
    matched_user_email = serializers.CharField(source = 'matched_user.email', read_only = True)
    matched_user_profile = serializers.ImageField(source = 'matched_user.profile_picture',read_only = True)
    skill_match_details = SkillMatchSerializer(source = 'skill_match', read_only = True)
    
    class Meta:
        model = SavedMatch
        fields = [
            'id','user','matched_user','matched_user_name',
            'matched_user_email','matched_user_profile',
            'skill_match','skill_match_details','notes','created_at'
        ]
        read_only_fields = ['id','user','created_at']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)