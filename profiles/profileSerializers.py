from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    UserProfile, Education, Experience, Certification,
    Project, Achievement, ProfileView, Follow, Block,
    ProfileReport, SocialLink
)
 
User = get_user_model()
 
 
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
 
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_email', 'user_name', 'headline', 'about',
            'website', 'linkedin_url', 'github_url', 'twitter_url', 'portfolio_url',
            'preferred_language', 'timezone', 'show_email', 'show_phone',
            'show_location', 'profile_visibility', 'email_notifications',
            'match_notifications', 'message_notifications', 'session_reminders',
            'profile_views', 'last_active', 'is_verified', 'verified_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'profile_views', 'is_verified', 'verified_at',
            'created_at', 'updated_at'
        ]
 
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
 