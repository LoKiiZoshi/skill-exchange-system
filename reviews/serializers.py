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
        
    def validate(self, attrs):
        # At least one of listing_id or reviewed_user must be set
        if not attrs.get('listing_id') and not attrs.get('reviewed_user'):
            raise serializers.ValidationError(
                "A review must target either a listing(listing_id) or a user(reviewed_user_id)."
            )
            return attrs
        
    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)
        
        
        

        
        