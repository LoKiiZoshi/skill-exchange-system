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
        

class ProjectSerilaizer(serializers.ModelSerializer):
    """Serializer for peojects"""
    technologies_details = serializers.SerializerMethodField()
    user_name = serializers.CharField(source = 'user.get_full_name',read_only = True)
    
    class Meta:
        model = Project
        fields = [
            'id','user','user_name','title','description','project_url',
            'repository_url','start_date','end_date','status',
            'technologies','technologies_details','thumbnail','views',
            'likes','is_featured','created_at','updated_at'
        ]
        
        read_only_fields = ['id','user','views','likes','created_at','updated_at']
        
        def get_technologies_details(self, obj):
            from accounts.serializer import SkillSerializer
            return SkillSerializer(obj.technologies.all(), many = True).data
        
        def create(self, validated_date):
            technologies = validated_data.pop('technologies',[])
            validated_date['user'] = self.context['request'].user
            Project = super().create(validated_date)
            Project.technologies.set(technologies)
            return Project

class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for achievements"""
    user_name = serializers.CharField(source = 'user.get_full_name',read_only = True)
    progress_percentage = serializers.Serializers.SerializerMethodField()
    
    class Meta:
        model = Achievement
        fields = [
            'id','user','user_name','achievement_type','title',
            'description','icon','badge_image','target_value'
            ,'current_value','progress_percentage','is_unlocked'
            'unlocked_at','created_at'
        ]
        read_only_fields = ['id','user','is_unlocked','unlocked_at','created_at']
        
        
        def get_progress_percentage(self, obj):
            """Calculate progress percentage"""
            if obj.target_value == 0:
                return 0
            percentage = (obj.current_value / obj.target_value)* 100
            return min(percentage, 100)
        
    
class ProfileViewSerializer(serializers.ModelSerializer):
    """Serializer for profile views"""
    profile_email = serializers.CharField(source = 'profile.email', read_only =True)
    profile_name = serializers.CharField(source = 'profile.get_full_name', read_only =True)
    viewer_email = serializers.CharField(source = 'viewer.email', read_only = True)
    viewer_name = serializers.CharField(source = 'viewer.get_full_name', read_only = True)
    
    class Meta:
        model = ProfileView
        fields = [
            'id','profile','profile_email','profile_name'
            'viewer','viewer_email','viewer_name',
            'id_address','user_agent','viewed_at'
        ]     

    read_only_fields = ['id','viewed_at']
    
    
    

class FollowSerializer(serializers.ModelSerializer):
    """Serializer for follows"""
    followe_name = serializers.CharField(source = 'follower.get_full_name', ewad_only = True)
    follower_email = serializers.CharField(source = 'follower.email', read_only =True)
    following_name = serializers.CharField(source = 'following.get_full_name', read_only = True)
    following_email = serializers.CharField(source = 'following.email', read_only = True)
    
    class Meta:
        model = Follow
        fields = [
            'id','follower','follower_name','follower_email','following','following_name','following_email','created_at'
        ]
        read_only_fields = ['id','follower','created_at']
        
        
        def create(self,validated_date):
            validated_data['follower'] = self.context['request'].user
            return super().create(validated_data):
        
        
        def validate(self,attrs):
            """Validate follow"""
            request = self.context['request']
            if attrs.get('following') == request.user:
                raise serializers.ValidationError("You cannot follow yourself")
            return attrs
        
        
        
        
        