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
            
            
            
class SkillMatchViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for skill matches"""
    serializer_class = SkillMatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['match_type','is_active']
    ordering_fields = ['match_score','created_at']
    ordering = ['-match_score']
    
    def get_queryset(self):
        """Return matches for current user"""
        user = self.request.user
        return SkillMatch.objects.filter(
            Q(user1 = user)| Q(user2 = user), is_active = True
        )
        
        
    @action(detail=False, methods=['get'])
    def top_matches(self , request):
        """Get top matches for current user"""
        limit = int(request.query_params.get('limit',10))
        matches = self.get_queryset().order_by('-match_score')[:limit]
        serializer = self.get_serializer(matches, many = True)
        return Response(serializer.data)
    
    
    @action(detail=True, methods=['post'])
    def mark_viewed(self, request,pk = None):
        """Mark match as viewed"""
        match = self.get_object()
        User = request.user
        
        if match.user1 == user:
            match.viewed_by_user1 = True
        elif match.user2 == User:
            match.viewed_by_user2 = True
            
        match.save()
        serializer = self.get_serializer(match)
        return Response(serializer.data)
    
    
    
    @action(detail=True,methods=['post'])
    def mark_interest(self, request, pk = None):
        """Mark interest in this match"""
        match = self.get_object()
        user = request.user
        
        if match.user1 == user:
            match.user1_interested = True
        elif match.user2 == user:
            match.user2_interested = True
        
        match.save()
        
        # if both interested, create notification 
        if match.user1_interested and match.user2_interested:
            from skills.models import Notification
            Notification.objects.create(
                user = match.user1 if user == match.user2 else match.user2,
                Notification_type = 'new_message',
                title = 'Mutual Match Interest!',
                message = f'{user.get_full_name()} is also interested in your match!'
            )
            
            serializer = self.get_serializer(match)
            return Response(serializer.data)
        
        
        
class MatchSuggestionViewSet(viewsets.ModelViewSet):
    """ViewSet for match suggestions"""
    serializer_class = MatchSuggestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['suggestion_score', 'created_at']
    ordering = ['-suggestion_score','-created_at']
    
    def get_queryset(self):
        """Return suggetions for current user"""
        return MatchSuggestion.objects.filter(user = self.request.user,dismissed = False)
    
    @action(detail=False, methods=['get'])
    def unviewed(self, request):
        """Get unviewed suggestions"""
        suggestions = self.get_queryset().filter(viewed = False)
        serializer = self.get_serializer(suggestions, many = True)
        return Response(serializer.data)
    
    @action(detail=True,methods=['post'])
    def mark_viewed(self, request, pk = None):
        """Mark suggestion as viewed"""
        suggestion = self.get_object()
        suggestion.mark_as_viewed()
        serializer = self.get_serializer(suggestion)
        return Response(serializer.data)
    
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk = None):
        """Dismiss this suggestion"""
        suggestion = self.get_object()
        suggestion.dismiss()
        serializer = self.get_serializer(suggestion)
        return Response(serializer.data)
    
    @action(detail=True, methods = ['post'])
    def accept(self, request, pk = None):
        """Accept this suggestion"""
        suggestion = self.get_object()
        suggestion.accept()
        serializer = self.get_serializer(suggestion)
        return Response(serializer.data)


class SavedMatchViewSet(viewsets.ModelViewSet):
    """ViewSet for saved matches"""
    serializer_class = SavedMatchSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return SavedMatch.objects.filter(User = self.request.user)
    
    
class MatchFilterViewSet(viewsets.ModelViewSet):
    """ViewSet for match filters"""
    serializer_class = MatchFilterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']
    
    
    def get_queryset(self):
        return MatchFilter.objects.filter(User = self.request.user)
    
    @action(detail=False,methods=['get'])
    def active(self, request):
        """Get active filters"""
        filters = self.get_queryset().filter(is_active = True)
        serializer = self.get_serializer(filters, many = True)
        return Response(serializer.data)
    
    @action(detail=True,methods = ['post'])
    def apply(self, request, pk = None):
        """Apply this filter and get matches"""
        match_filter = self.get_object()
        
        
        # Get users based on filter criteria
        users = users.objects.exclude(id = request.user.id)
        
        # Filter by skills
        if match_filter.skills.exists():
            users = users.filter(
                user_skills___skill_in = match_filter.skills.all(),
                user_skills__can_teach = True
            ).distinct()
            
            
        # Filter by skill categories
        if match_filter.skill_categories.exists():
            users = users.filter(
                user_skills___skill_category__in = match_filter.skill_categories.all(),
                user_skillls___can_teach = True
            ).distinct()
            
            #Filter by rating
            if match_filter.min_rating:
                users = users.annotate(
                    avg_rating = Avg('ratings_received__rating')
                )
                
                # Filter by location
                if match_filter.location:
                    users = users.filter(location___icontains = match_filter.location)
                    
                    from accounts.serializers import UserProfileSerializer
                    serilaizer = UserProfileSerializer(users,many = True)
                    return Response(serilaizer.data)
                
                
                
                