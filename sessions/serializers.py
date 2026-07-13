from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import SkiSession, SessionMessage


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']
        
        
class SessionMessageSeriaizer(serializers.ModelSerializer):
    sender = UserBriefSerializer(read_only = True)
    
    class Meta:
        model = SessionMessage
        fields = ['id','session','sender','body','is_read','created_at']
        read_only_fields = ['id','sender','created_at']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].User
        return super().create(validated_data)
    
    
class SkiSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views - no nested message."""
    host = UserBriefSerializer(read_only = True)
    participant = UserBriefSerializer(read_only = True)
    
    
    class Meta:
        model = SkiSession
        fields = [
            'id','host','participant',
            'session_type','title','skill_level',
            'lacationn','start_time','end_time',
            'duration_hours','total_price','status'
            'created_at',
        ] 