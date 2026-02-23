from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    ExchangeRequest, ExchangeSession, SessionFeedback,
    SkillExchangeOffer, Booking, Notification
)

User = get_user_model()


class ExchangeRequestSerializer(serializers.ModelSerializer):
    """Serializer for exchange requests"""
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.get_full_name', read_only=True)
    skill_offered_name = serializers.CharField(source='skill_offered.name', read_only=True)
    skill_requested_name = serializers.CharField(source='skill_requested.name', read_only=True)

    class Meta:
        model = ExchangeRequest
        fields = [
            'id', 'requester', 'requester_name', 'receiver', 'receiver_name',
            'skill_offered', 'skill_offered_name', 'skill_requested',
            'skill_requested_name', 'status', 'message', 'response_message',
            'proposed_date', 'duration_minutes', 'created_at', 'updated_at',
            'responded_at'
        ]
        read_only_fields = ['id', 'requester', 'created_at', 'updated_at', 'responded_at']

    def create(self, validated_data):
        validated_data['requester'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        request = self.context['request']
        
        # Can't send request to yourself
        if attrs.get('receiver') == request.user:
            raise serializers.ValidationError("You cannot send an exchange request to yourself.")
        
        # Check if user has the skill they're offering
        if self.instance is None:  # Only on creation
            skill_offered = attrs.get('skill_offered')
            if not request.user.user_skills.filter(skill=skill_offered, can_teach=True).exists():
                raise serializers.ValidationError(
                    "You must have the skill you're offering marked as teachable."
                )
        
        return attrs


class ExchangeRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating exchange request status"""
    class Meta:
        model = ExchangeRequest
        fields = ['status', 'response_message']

    def validate_status(self, value):
        if value not in ['accepted', 'rejected', 'cancelled']:
            raise serializers.ValidationError(
                "Status can only be updated to 'accepted', 'rejected', or 'cancelled'."
            )
        return value

    def update(self, instance, validated_data):
        instance.responded_at = timezone.now()
        return super().update(instance, validated_data)


class ExchangeSessionSerializer(serializers.ModelSerializer):
    """Serializer for exchange sessions"""
    participant_1_name = serializers.CharField(source='participant_1.get_full_name', read_only=True)
    participant_2_name = serializers.CharField(source='participant_2.get_full_name', read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = ExchangeSession
        fields = [
            'id', 'exchange_request', 'participant_1', 'participant_1_name',
            'participant_2', 'participant_2_name', 'title', 'description',
            'status', 'meeting_type', 'scheduled_start', 'scheduled_end',
            'actual_start', 'actual_end', 'meeting_link', 'location',
            'notes', 'participant_1_notes', 'participant_2_notes',
            'duration_minutes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        # Ensure scheduled_end is after scheduled_start
        if attrs.get('scheduled_start') and attrs.get('scheduled_end'):
            if attrs['scheduled_end'] <= attrs['scheduled_start']:
                raise serializers.ValidationError(
                    "Scheduled end time must be after start time."
                )
        
        # Validate actual times if provided
        if attrs.get('actual_start') and attrs.get('actual_end'):
            if attrs['actual_end'] <= attrs['actual_start']:
                raise serializers.ValidationError(
                    "Actual end time must be after start time."
                )
        
        return attrs


class SessionFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for session feedback"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    session_title = serializers.CharField(source='session.title', read_only=True)

    class Meta:
        model = SessionFeedback
        fields = [
            'id', 'session', 'session_title', 'user', 'user_name',
            'overall_rating', 'teaching_quality', 'communication',
            'punctuality', 'what_went_well', 'what_to_improve',
            'additional_comments', 'would_recommend', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        request = self.context['request']
        session = attrs.get('session')
        
        # Check if user is a participant
        if request.user not in [session.participant_1, session.participant_2]:
            raise serializers.ValidationError(
                "You can only provide feedback for sessions you participated in."
            )
        
        # Check if session is completed
        if session.status != 'completed':
            raise serializers.ValidationError(
                "Feedback can only be provided for completed sessions."
            )
        
        return attrs


class SkillExchangeOfferSerializer(serializers.ModelSerializer):
    """Serializer for skill exchange offers"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    desired_skills_details = serializers.SerializerMethodField()

    class Meta:
        model = SkillExchangeOffer
        fields = [
            'id', 'user', 'user_name', 'skill', 'skill_name', 'title',
            'description', 'prerequisites', 'status', 'max_students',
            'session_duration', 'availability', 'preferred_meeting_type',
            'requires_exchange', 'desired_skills', 'desired_skills_details',
            'total_sessions', 'total_students', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'total_sessions', 'total_students', 'created_at', 'updated_at']

    def get_desired_skills_details(self, obj):
        from accounts.serializers import SkillSerializer
        return SkillSerializer(obj.desired_skills.all(), many=True).data

    def create(self, validated_data):
        desired_skills = validated_data.pop('desired_skills', [])
        validated_data['user'] = self.context['request'].user
        offer = super().create(validated_data)
        offer.desired_skills.set(desired_skills)
        return offer


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for bookings"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    offer_title = serializers.CharField(source='offer.title', read_only=True)
    teacher_name = serializers.CharField(source='offer.user.get_full_name', read_only=True)
    exchange_skill_name = serializers.CharField(source='exchange_skill.name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'offer', 'offer_title', 'teacher_name', 'student',
            'student_name', 'status', 'message', 'proposed_datetime',
            'exchange_skill', 'exchange_skill_name', 'exchange_message',
            'session', 'created_at', 'updated_at', 'confirmed_at'
        ]
        read_only_fields = ['id', 'student', 'session', 'created_at', 'updated_at', 'confirmed_at']

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        request = self.context['request']
        offer = attrs.get('offer')
        
        # Can't book your own offer
        if offer and offer.user == request.user:
            raise serializers.ValidationError("You cannot book your own offer.")
        
        # Check if offer requires exchange and exchange_skill is provided
        if offer and offer.requires_exchange and not attrs.get('exchange_skill'):
            raise serializers.ValidationError(
                "This offer requires a skill exchange. Please provide a skill you can teach."
            )
        
        # Check if offer is active
        if offer and offer.status != 'active':
            raise serializers.ValidationError("This offer is not currently active.")
        
        return attrs


class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating booking status"""
    class Meta:
        model = Booking
        fields = ['status']

    def validate_status(self, value):
        if value not in ['confirmed', 'cancelled']:
            raise serializers.ValidationError(
                "Status can only be updated to 'confirmed' or 'cancelled'."
            )
        return value

    def update(self, instance, validated_data):
        if validated_data.get('status') == 'confirmed':
            instance.confirmed_at = timezone.now()
        return super().update(instance, validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'title', 'message',
            'exchange_request', 'session', 'booking', 'is_read',
            'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class ExchangeSessionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for exchange sessions with feedback"""
    participant_1_name = serializers.CharField(source='participant_1.get_full_name', read_only=True)
    participant_2_name = serializers.CharField(source='participant_2.get_full_name', read_only=True)
    feedbacks = SessionFeedbackSerializer(many=True, read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = ExchangeSession
        fields = [
            'id', 'exchange_request', 'participant_1', 'participant_1_name',
            'participant_2', 'participant_2_name', 'title', 'description',
            'status', 'meeting_type', 'scheduled_start', 'scheduled_end',
            'actual_start', 'actual_end', 'meeting_link', 'location',
            'notes', 'participant_1_notes', 'participant_2_notes',
            'duration_minutes', 'feedbacks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SkillExchangeOfferDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for offers with bookings"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    desired_skills_details = serializers.SerializerMethodField()
    bookings = BookingSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = SkillExchangeOffer
        fields = [
            'id', 'user', 'user_name', 'skill', 'skill_name', 'title',
            'description', 'prerequisites', 'status', 'max_students',
            'session_duration', 'availability', 'preferred_meeting_type',
            'requires_exchange', 'desired_skills', 'desired_skills_details',
            'total_sessions', 'total_students', 'bookings', 'average_rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'total_sessions', 'total_students', 'created_at', 'updated_at']

    def get_desired_skills_details(self, obj):
        from accounts.serializers import SkillSerializer
        return SkillSerializer(obj.desired_skills.all(), many=True).data

    def get_average_rating(self, obj):
        # Calculate average rating from session feedbacks
        sessions = ExchangeSession.objects.filter(
            exchange_request__skill_offered=obj.skill,
            status='completed'
        )
        feedbacks = SessionFeedback.objects.filter(session__in=sessions)
        if feedbacks.exists():
            return round(sum(f.overall_rating for f in feedbacks) / feedbacks.count(), 2)
        return None