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
        
           
class SkiSessionSerializer(serializers.ModelSerializer):
    host = UserBriefSerializer(read_only = True)
    participant = UserBriefSerializer(read_only = True)
     
    # Write-only fields for setting host / participant by ID
    host_id = serializers.PrimaryKeyRelatedField(queryset = User.objects.all(), source ='participant', write_only = True, required = False)
    participant_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all().sorce = 'host',
        write_only = True, required = False
    )
    
    
    # Computed / read-only
    duration_hours = serializers.DecimalField(max_digits=5,decimal_places=2, read_only = True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only = True)
    messages = SessionMessageSeriaizer(many =True, read_only =True)
    
    class Meta:
        model = SkiSessionfields = [
            'id',
            'host','host_id'
            ,'participant','participant_id',
            'session_type','title','description','skill_level',
            'listing_id','listing_title','location','latitude','longitude',
            'start_time','end_time','duration_hours',
            'price_per_hour','total_price',
            'status','cancellation_reason',
            'host_notes','participant_notes',
        ]
        
        read_only_fields = ['id','duration_hours','total_price','created_at','updated_at']
        
    def validate(self, attrs):
        start = attrs.get('start_time')
        end = attrs.get('end_time')
        
        if start and end:
            if end <= start:
                raise serializers.ValidationError("end time must be after start_time")
            if start < timezone.now() and self.instance is None:
                raise serializers.ValidationError("Cannot create a sesssion in the past.")
            return attrs
        
        def create(self, validated_data):
            # Default host to the requesting user if not explicitly provided 
            if 'host' not in validated_data:
                validated_data['host'] = self.context['request'].user
                return super().create(validated_data)
            
            
            