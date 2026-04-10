from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q,Avg,Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
import math

from accounts.models import Skill,UserSkill,SkillWanted
from .models import(
    MatchPreference, SkillMatch, MatchSuggestion,SavedMatch, MatchFilter,MatchAnalytics,MatchFeedback
)

from .serializers import(
     MatchPreferenceSerializer, SkillMatchSerializer,
    MatchSuggestionSerializer, SavedMatchSerializer,
    MatchFilterSerializer, MatchAnalyticsSerializer,
    MatchFeedbackSerializer, MatchingAlgorithmInputSerializer,
    BulkMatchGenerationSerializer
)

User = get_user_model()


class MatchPrePreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for match preference"""
    serializer_class = MatchPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MatchPreference.objects.filter(User = self.request.user)
    
    
    @action(detail=False, method = ['get','post','put'])
    def my_preferences(self, request):
        """Get or update current user's preferences"""
        try:
             preference = MatchPreference.objects.get(user = request.User)
        except MatchPreference.DoesNotExist:
            if request.method == 'GET':
                return Response(
                    {'error':'Preferences not set'},
                    status= status.HTTP_404_NOT_FOUND
                )
            preference = None
            
        if request.method = 'GET':
            serializer = self.get_serializer(serializer)
            return Response(serializer.data)
        
        
        if request.method in ['POST', 'PUT']:
            if preference:
                serializer = self.get_serializer(preference,data = request.data, partial = True)
            else:
                serializer = self.get_serializer(data = request.data)
                
                serializer.is_valid(raise_exception = True)
                serializer.save()
                return Response(serializer.data)