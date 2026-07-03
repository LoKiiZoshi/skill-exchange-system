from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Review

class ReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']
        
        
class ReviewSerializer(serializers.ModelSerializer):
    reviewer = ReviewerSerializer(read_only = True)
    reviewed_user = ReviewerSerializer(read_only = True)
    reviewed_user_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(),source = 'reviewed_user',
        write_only = True,required = False, allow_null = True
    )
    
    class Meta:
        model = Review
        fields = [
            'id','reviewer',
            'reviewed_user','reviewed_user_id',
            'listing_id','listing_title',
            'rating','title','body',
            'created_at','updated_at'
        ]
        
        read_only_fields = ['id','reviewer','created_at','updated_at']
        
        
        