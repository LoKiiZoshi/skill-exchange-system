from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
import math

from accounts.models import Skill, UserSkill, SkillWanted
from .models import (
    MatchPreference, SkillMatch, MatchSuggestion,
    SavedMatch, MatchFilter, MatchAnalytics, MatchFeedback
)
from .serializers import (
    MatchPreferenceSerializer, SkillMatchSerializer,
    MatchSuggestionSerializer, SavedMatchSerializer,
    MatchFilterSerializer, MatchAnalyticsSerializer,
    MatchFeedbackSerializer, MatchingAlgorithmInputSerializer,
    BulkMatchGenerationSerializer
)

User = get_user_model()


class MatchPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for match preferences"""
    serializer_class = MatchPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MatchPreference.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get', 'post', 'put'])
    def my_preferences(self, request):
        """Get or update current user's preferences"""
        try:
            preference = MatchPreference.objects.get(user=request.user)
        except MatchPreference.DoesNotExist:
            if request.method == 'GET':
                return Response(
                    {'error': 'Preferences not set'},
                    status=status.HTTP_404_NOT_FOUND
                )
            preference = None

        if request.method == 'GET':
            serializer = self.get_serializer(preference)
            return Response(serializer.data)
        
        if request.method in ['POST', 'PUT']:
            if preference:
                serializer = self.get_serializer(preference, data=request.data, partial=True)
            else:
                serializer = self.get_serializer(data=request.data)
            
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class SkillMatchViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for skill matches"""
    serializer_class = SkillMatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['match_type', 'is_active']
    ordering_fields = ['match_score', 'created_at']
    ordering = ['-match_score']

    def get_queryset(self):
        """Return matches for current user"""
        user = self.request.user
        return SkillMatch.objects.filter(
            Q(user1=user) | Q(user2=user),
            is_active=True
        )

    @action(detail=False, methods=['get'])
    def top_matches(self, request):
        """Get top matches for current user"""
        limit = int(request.query_params.get('limit', 10))
        matches = self.get_queryset().order_by('-match_score')[:limit]
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Mark match as viewed"""
        match = self.get_object()
        user = request.user
        
        if match.user1 == user:
            match.viewed_by_user1 = True
        elif match.user2 == user:
            match.viewed_by_user2 = True
        
        match.save()
        serializer = self.get_serializer(match)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_interested(self, request, pk=None):
        """Mark interest in this match"""
        match = self.get_object()
        user = request.user
        
        if match.user1 == user:
            match.user1_interested = True
        elif match.user2 == user:
            match.user2_interested = True
        
        match.save()
        
        # If both interested, create notification
        if match.user1_interested and match.user2_interested:
            from skills.models import Notification
            Notification.objects.create(
                user=match.user1 if user == match.user2 else match.user2,
                notification_type='new_message',
                title='Mutual Match Interest!',
                message=f'{user.get_full_name()} is also interested in your match!'
            )
        
        serializer = self.get_serializer(match)
        return Response(serializer.data)


class MatchSuggestionViewSet(viewsets.ModelViewSet):
    """ViewSet for match suggestions"""
    serializer_class = MatchSuggestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['suggestion_type', 'viewed', 'dismissed', 'accepted']
    ordering_fields = ['suggestion_score', 'created_at']
    ordering = ['-suggestion_score', '-created_at']

    def get_queryset(self):
        """Return suggestions for current user"""
        return MatchSuggestion.objects.filter(
            user=self.request.user,
            dismissed=False
        )

    @action(detail=False, methods=['get'])
    def unviewed(self, request):
        """Get unviewed suggestions"""
        suggestions = self.get_queryset().filter(viewed=False)
        serializer = self.get_serializer(suggestions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Mark suggestion as viewed"""
        suggestion = self.get_object()
        suggestion.mark_as_viewed()
        serializer = self.get_serializer(suggestion)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss this suggestion"""
        suggestion = self.get_object()
        suggestion.dismiss()
        serializer = self.get_serializer(suggestion)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
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
        return SavedMatch.objects.filter(user=self.request.user)


class MatchFilterViewSet(viewsets.ModelViewSet):
    """ViewSet for match filters"""
    serializer_class = MatchFilterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        return MatchFilter.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active filters"""
        filters = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(filters, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply this filter and get matches"""
        match_filter = self.get_object()
        
        # Get users based on filter criteria
        users = User.objects.exclude(id=request.user.id)
        
        # Filter by skills
        if match_filter.skills.exists():
            users = users.filter(
                user_skills__skill__in=match_filter.skills.all(),
                user_skills__can_teach=True
            ).distinct()
        
        # Filter by skill categories
        if match_filter.skill_categories.exists():
            users = users.filter(
                user_skills__skill__category__in=match_filter.skill_categories.all(),
                user_skills__can_teach=True
            ).distinct()
        
        # Filter by rating
        if match_filter.min_rating:
            users = users.annotate(
                avg_rating=Avg('ratings_received__rating')
            ).filter(avg_rating__gte=match_filter.min_rating)
        
        # Filter by location
        if match_filter.location:
            users = users.filter(location__icontains=match_filter.location)
        
        from accounts.serializers import UserProfileSerializer
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)


class MatchFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for match feedback"""
    serializer_class = MatchFeedbackSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']

    def get_queryset(self):
        return MatchFeedback.objects.filter(user=self.request.user)


class FindMatchesView(APIView):
    """View for finding matches using intelligent algorithm"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Find matches for a specific skill"""
        serializer = MatchingAlgorithmInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        skill_id = serializer.validated_data['skill_id']
        max_results = serializer.validated_data['max_results']
        include_one_way = serializer.validated_data['include_one_way']
        min_score = serializer.validated_data['min_match_score']
        
        try:
            skill = Skill.objects.get(id=skill_id)
        except Skill.DoesNotExist:
            return Response(
                {'error': 'Skill not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find matches
        matches = self._find_matches(
            request.user,
            skill,
            max_results,
            include_one_way,
            min_score
        )
        
        return Response({
            'skill': skill.name,
            'total_matches': len(matches),
            'matches': matches
        })

    def _find_matches(self, user, skill, max_results, include_one_way, min_score):
        """Core matching algorithm"""
        matches = []
        
        # Get user's wanted skills
        wanted_skills = SkillWanted.objects.filter(user=user).values_list('skill_id', flat=True)
        
        # Find users who want to learn this skill
        potential_matches = UserSkill.objects.filter(
            skill=skill,
            can_teach=True
        ).exclude(user=user)
        
        for user_skill in potential_matches:
            other_user = user_skill.user
            
            # Calculate match score
            score_data = self._calculate_match_score(user, other_user, skill, wanted_skills)
            
            if score_data['total_score'] >= min_score:
                matches.append({
                    'user': {
                        'id': other_user.id,
                        'name': other_user.get_full_name(),
                        'email': other_user.email,
                        'location': other_user.location,
                        'profile_picture': other_user.profile_picture.url if other_user.profile_picture else None
                    },
                    'skill_offered': skill.name,
                    'skill_requested': score_data.get('mutual_skill'),
                    'match_score': score_data['total_score'],
                    'match_type': score_data['match_type'],
                    'compatibility_breakdown': {
                        'skill': score_data['skill_score'],
                        'location': score_data['location_score'],
                        'experience': score_data['experience_score'],
                        'rating': score_data['rating_score']
                    }
                })
        
        # Sort by score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matches[:max_results]

    def _calculate_match_score(self, user1, user2, skill, wanted_skills):
        """Calculate compatibility score between two users"""
        scores = {
            'skill_score': 0,
            'location_score': 0,
            'experience_score': 0,
            'rating_score': 0,
            'total_score': 0,
            'match_type': 'one_way_teaching',
            'mutual_skill': None
        }
        
        # 1. Skill compatibility (40 points)
        user2_skills = UserSkill.objects.filter(user=user2, can_teach=True)
        mutual_skills = user2_skills.filter(skill_id__in=wanted_skills)
        
        if mutual_skills.exists():
            scores['match_type'] = 'mutual_exchange'
            scores['skill_score'] = 40
            scores['mutual_skill'] = mutual_skills.first().skill.name
        else:
            scores['skill_score'] = 20
        
        # 2. Location compatibility (20 points)
        if user1.location and user2.location:
            if user1.location.lower() == user2.location.lower():
                scores['location_score'] = 20
            elif any(word in user2.location.lower() for word in user1.location.lower().split()):
                scores['location_score'] = 10
        
        # 3. Experience compatibility (20 points)
        user_skill = UserSkill.objects.filter(user=user2, skill=skill).first()
        if user_skill:
            years = user_skill.years_of_experience
            if years >= 5:
                scores['experience_score'] = 20
            elif years >= 2:
                scores['experience_score'] = 15
            elif years >= 1:
                scores['experience_score'] = 10
            else:
                scores['experience_score'] = 5
        
        # 4. Rating compatibility (20 points)
        ratings = user2.ratings_received.all()
        if ratings.exists():
            avg_rating = sum(r.rating for r in ratings) / ratings.count()
            scores['rating_score'] = int((avg_rating / 5.0) * 20)
        
        # Calculate total
        scores['total_score'] = sum([
            scores['skill_score'],
            scores['location_score'],
            scores['experience_score'],
            scores['rating_score']
        ])
        
        return scores


class GenerateMatchesView(APIView):
    """View for bulk match generation"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Generate matches for user"""
        serializer = BulkMatchGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data.get('user_id')
        regenerate = serializer.validated_data['regenerate_existing']
        min_score = serializer.validated_data['min_score_threshold']
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            user = request.user
        
        # Delete existing if regenerating
        if regenerate:
            SkillMatch.objects.filter(Q(user1=user) | Q(user2=user)).delete()
        
        # Generate new matches
        created_count = self._generate_matches_for_user(user, min_score)
        
        return Response({
            'message': f'Generated {created_count} matches',
            'user': user.email,
            'total_matches': created_count
        })

    def _generate_matches_for_user(self, user, min_score):
        """Generate matches for a specific user"""
        created = 0
        
        # Get user's skills they can teach
        user_skills = UserSkill.objects.filter(user=user, can_teach=True)
        
        for user_skill in user_skills:
            # Find potential matches
            wanted_by = SkillWanted.objects.filter(
                skill=user_skill.skill
            ).exclude(user=user)
            
            for wanted in wanted_by:
                other_user = wanted.user
                
                # Check if match already exists
                if SkillMatch.objects.filter(
                    Q(user1=user, user2=other_user) | Q(user1=other_user, user2=user)
                ).exists():
                    continue
                
                # Calculate scores
                score_calculator = FindMatchesView()
                wanted_skills = SkillWanted.objects.filter(user=user).values_list('skill_id', flat=True)
                scores = score_calculator._calculate_match_score(
                    user, other_user, user_skill.skill, wanted_skills
                )
                
                if scores['total_score'] >= min_score:
                    # Determine mutual skill
                    mutual_skill = None
                    if scores['match_type'] == 'mutual_exchange':
                        mutual_skills = UserSkill.objects.filter(
                            user=other_user,
                            skill_id__in=wanted_skills,
                            can_teach=True
                        )
                        if mutual_skills.exists():
                            mutual_skill = mutual_skills.first().skill
                    
                    # Create match
                    SkillMatch.objects.create(
                        user1=user,
                        user2=other_user,
                        user1_skill=user_skill.skill,
                        user2_skill=mutual_skill,
                        match_type=scores['match_type'],
                        match_score=scores['total_score'],
                        skill_compatibility=scores['skill_score'],
                        location_compatibility=scores['location_score'],
                        experience_compatibility=scores['experience_score'],
                        rating_compatibility=scores['rating_score']
                    )
                    created += 1
        
        return created


class MatchStatisticsView(APIView):
    """View for match statistics"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get matching statistics for current user"""
        user = request.user
        
        stats = {
            'total_matches': SkillMatch.objects.filter(
                Q(user1=user) | Q(user2=user),
                is_active=True
            ).count(),
            'mutual_exchange_matches': SkillMatch.objects.filter(
                Q(user1=user) | Q(user2=user),
                match_type='mutual_exchange',
                is_active=True
            ).count(),
            'one_way_matches': SkillMatch.objects.filter(
                Q(user1=user) | Q(user2=user),
                match_type='one_way_teaching',
                is_active=True
            ).count(),
            'average_match_score': SkillMatch.objects.filter(
                Q(user1=user) | Q(user2=user),
                is_active=True
            ).aggregate(Avg('match_score'))['match_score__avg'] or 0,
            'unviewed_matches': SkillMatch.objects.filter(
                Q(user1=user, viewed_by_user1=False) |
                Q(user2=user, viewed_by_user2=False),
                is_active=True
            ).count(),
            'mutual_interest': SkillMatch.objects.filter(
                Q(user1=user) | Q(user2=user),
                user1_interested=True,
                user2_interested=True,
                is_active=True
            ).count(),
            'saved_matches': SavedMatch.objects.filter(user=user).count(),
            'active_suggestions': MatchSuggestion.objects.filter(
                user=user,
                dismissed=False
            ).count(),
            'has_preferences': MatchPreference.objects.filter(user=user).exists()
        }
        
        return Response(stats)