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
 
 
 


class EducationSerializer(serializers.ModelSerializer):
    """Serializer for education"""
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Education
        fields = [
            'id','user','institution','degree','fields_of_study',
            'start_date','end_date','is_current','grade','description',
            'duration','created_at','updated_at'
        ]
        
        read_only_fields = ['id','user','created_at','updated_at']
        
        
        def get_duration(self,obj):
            """Calculate duration of education"""
            start = obj.start_date
            end = obj.end_date if obj.end_date else timezone.now().date()
            years = (end - start).days / 365.25
            return f"{years:.1f} years"
        
        
        def create(self, validated_data):
            validated_data['user'] = self.context['request'].user
            return  super().create(validated_data)
        
        def validate(self,attrs):
         """Validate dates"""
         if attrs.get('end_date') and attrs.get('start_date'):
             if attrs['end_date'] < attrs['start_date']:
                 raise serializers.ValidationError("End date must be after start date")
             return attrs
         
class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for work experience"""
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Experience
        fields = [
            'id','user','title','company','employment_type','location',
            'start_date','end_date','is_current','description',
            'duration', 'created_at','updated_at'
        ]
        
        read_only_fileds = ['id','user','created_at','updated_at']
        
        def get_duration(self, obj):
            """Calculate duration of experience"""
            start = obj.start_date
            end  = obj.end_date if obj.end_date else timezone.now().date()
            years = (end - start).days / 365.25
            return f"{years:1f}years"
        def create(self, validated_data):
            validated_data['user'] = self.context['request'].user
            return super().create(validated_data)
        
        def validate(self, attrs):
            """Validate dates"""
            if attrs.get('end_date') and attrs.get('start_date'):
                if attrs['end_date']< attrs['start_date']:
                    raise serializers.ValidationError("End date must be after start date")
                return attrs
            
class CertificationSerializer(serializers.ModelSerializer):
    """Serializer for certifications"""
    is_expired = serializers.BooleanField(read_only = True)
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Certification
        fields = [
            'id', 'user','name','issuing_organization','credential_id',
            'credential_url','issue_date','expiration_date','does_not_expire',
            'description','is_expired','status','created_at','updated_at'
        ]
        
        read_only_fields = ['id','user','created_at','updated_at']
        
        def get_status(self,obj):
            """Get certification status"""
            if obj.is_expired = serializers.BooleanField(read_only = True)
            status = serializers.SerializerMethodField()
            
            class Meta:
                model = Certification
                fields = [
                    'id','user','name','issuing_organization','credential_id'
                    ,'credential_url','issue_date','expiration_date','does_not_expire',
                    'description','is_expired','status','created_at','updated_at'
                ]
                
                read_only_fields =['id','user','created_at','updated_at']
                
                def get_status(self , obj):
                    """Get certification status"""
            if obj.is_expired:
                    return 'expired'
            elif obj.does_not_expire:
                return 'valid'
            elif obj.expiration_date:
                day_until_expiry = (obj.expiration_date - timezone.now().date()).days
                if days_until_expiry <= 30:
                    return 'expiring_soon'
                return 'valid'
            return 'valid'
        
        def create(self, validated_data):
            validated_data['user'] = self.context['request'].user
            return super().create(validated_data)