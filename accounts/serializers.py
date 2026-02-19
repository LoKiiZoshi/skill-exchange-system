from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    SkillCategory, Skill, UserSkill, SkillWanted, UserRating
)

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'bio', 'location', 'phone_number',
            'date_of_birth'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with skills"""
    full_name = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'first_name', 'last_name',
            'bio', 'profile_picture', 'location', 'phone_number',
            'date_of_birth', 'is_email_verified', 'average_rating',
            'total_ratings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'is_email_verified', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_average_rating(self, obj):
        ratings = obj.ratings_received.all()
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 2)
        return None

    def get_total_ratings(self, obj):
        return obj.ratings_received.count()


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs


class SkillCategorySerializer(serializers.ModelSerializer):
    """Serializer for skill categories"""
    skills_count = serializers.SerializerMethodField()

    class Meta:
        model = SkillCategory
        fields = ['id', 'name', 'description', 'icon', 'skills_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_skills_count(self, obj):
        return obj.skills.count()


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for skills"""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'category_name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSkillSerializer(serializers.ModelSerializer):
    """Serializer for user skills"""
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    category_name = serializers.CharField(source='skill.category.name', read_only=True)

    class Meta:
        model = UserSkill
        fields = [
            'id', 'user', 'skill', 'skill_name', 'category_name',
            'proficiency_level', 'years_of_experience', 'can_teach',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SkillWantedSerializer(serializers.ModelSerializer):
    """Serializer for skills wanted to learn"""
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    category_name = serializers.CharField(source='skill.category.name', read_only=True)

    class Meta:
        model = SkillWanted
        fields = [
            'id', 'user', 'skill', 'skill_name', 'category_name',
            'priority', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserRatingSerializer(serializers.ModelSerializer):
    """Serializer for user ratings"""
    rated_by_name = serializers.CharField(source='rated_by.get_full_name', read_only=True)
    rated_user_name = serializers.CharField(source='rated_user.get_full_name', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = UserRating
        fields = [
            'id', 'rated_user', 'rated_user_name', 'rated_by',
            'rated_by_name', 'rating', 'review', 'skill', 'skill_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'rated_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['rated_by'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        request = self.context['request']
        if attrs['rated_user'] == request.user:
            raise serializers.ValidationError("You cannot rate yourself.")
        return attrs


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with all related data"""
    full_name = serializers.SerializerMethodField()
    user_skills = UserSkillSerializer(many=True, read_only=True)
    skills_wanted = SkillWantedSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()
    ratings_received = UserRatingSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'first_name', 'last_name',
            'bio', 'profile_picture', 'location', 'phone_number',
            'date_of_birth', 'is_email_verified', 'user_skills',
            'skills_wanted', 'average_rating', 'total_ratings',
            'ratings_received', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'is_email_verified', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_average_rating(self, obj):
        ratings = obj.ratings_received.all()
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 2)
        return None

    def get_total_ratings(self, obj):
        return obj.ratings_received.count()