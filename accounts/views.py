from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    SkillCategory, Skill, UserSkill, SkillWanted, UserRating
)
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer,
    UserDetailSerializer, ChangePasswordSerializer,
    SkillCategorySerializer, SkillSerializer,
    UserSkillSerializer, SkillWantedSerializer,
    UserRatingSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'message': 'User registered successfully. Please verify your email.'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDetailView(generics.RetrieveAPIView):
    """View for retrieving detailed user information"""
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]


class ChangePasswordView(APIView):
    """View for changing password"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.data.get('old_password')):
                return Response(
                    {'old_password': ['Wrong password.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            return Response(
                {'message': 'Password updated successfully.'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkillCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for skill categories"""
    queryset = SkillCategory.objects.all()
    serializer_class = SkillCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def skills(self, request, pk=None):
        """Get all skills in a category"""
        category = self.get_object()
        skills = category.skills.all()
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)


class SkillViewSet(viewsets.ModelViewSet):
    """ViewSet for skills"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['category', 'name']

    @action(detail=True, methods=['get'])
    def users_with_skill(self, request, pk=None):
        """Get all users who have this skill"""
        skill = self.get_object()
        user_skills = UserSkill.objects.filter(skill=skill, can_teach=True)
        serializer = UserSkillSerializer(user_skills, many=True)
        return Response(serializer.data)


class UserSkillViewSet(viewsets.ModelViewSet):
    """ViewSet for user skills"""
    serializer_class = UserSkillSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['proficiency_level', 'can_teach', 'skill__category']
    ordering_fields = ['proficiency_level', 'years_of_experience', 'created_at']
    ordering = ['-proficiency_level', '-years_of_experience']

    def get_queryset(self):
        """Return skills for the current user or filter by user_id"""
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            return UserSkill.objects.filter(user_id=user_id)
        return UserSkill.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_skills(self, request):
        """Get current user's skills"""
        skills = UserSkill.objects.filter(user=request.user)
        serializer = self.get_serializer(skills, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def teachable_skills(self, request):
        """Get skills that user can teach"""
        skills = UserSkill.objects.filter(user=request.user, can_teach=True)
        serializer = self.get_serializer(skills, many=True)
        return Response(serializer.data)


class SkillWantedViewSet(viewsets.ModelViewSet):
    """ViewSet for skills wanted to learn"""
    serializer_class = SkillWantedSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['priority', 'skill__category']
    ordering_fields = ['priority', 'created_at']
    ordering = ['-priority', '-created_at']

    def get_queryset(self):
        """Return wanted skills for the current user or filter by user_id"""
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            return SkillWanted.objects.filter(user_id=user_id)
        return SkillWanted.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_wanted_skills(self, request):
        """Get current user's wanted skills"""
        skills = SkillWanted.objects.filter(user=request.user)
        serializer = self.get_serializer(skills, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def find_matches(self, request):
        """Find users who can teach the skills current user wants to learn"""
        wanted_skills = SkillWanted.objects.filter(user=request.user)
        wanted_skill_ids = [ws.skill.id for ws in wanted_skills]
        
        matches = UserSkill.objects.filter(
            skill_id__in=wanted_skill_ids,
            can_teach=True
        ).exclude(user=request.user)
        
        serializer = UserSkillSerializer(matches, many=True)
        return Response(serializer.data)


class UserRatingViewSet(viewsets.ModelViewSet):
    """ViewSet for user ratings"""
    serializer_class = UserRatingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rated_user', 'rating', 'skill']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return ratings based on query parameters"""
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            return UserRating.objects.filter(rated_user_id=user_id)
        return UserRating.objects.all()

    @action(detail=False, methods=['get'])
    def my_ratings(self, request):
        """Get ratings received by current user"""
        ratings = UserRating.objects.filter(rated_user=request.user)
        serializer = self.get_serializer(ratings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ratings_given(self, request):
        """Get ratings given by current user"""
        ratings = UserRating.objects.filter(rated_by=request.user)
        serializer = self.get_serializer(ratings, many=True)
        return Response(serializer.data)


class SearchUsersView(APIView):
    """View for searching users by various criteria"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')
        skill_id = request.query_params.get('skill_id', None)
        category_id = request.query_params.get('category_id', None)
        location = request.query_params.get('location', '')
        min_rating = request.query_params.get('min_rating', None)
        
        users = User.objects.all()
        
        # Search by name, email, or username
        if query:
            users = users.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(bio__icontains=query)
            )
        
        # Filter by skill
        if skill_id:
            users = users.filter(
                user_skills__skill_id=skill_id,
                user_skills__can_teach=True
            )
        
        # Filter by category
        if category_id:
            users = users.filter(
                user_skills__skill__category_id=category_id,
                user_skills__can_teach=True
            )
        
        # Filter by location
        if location:
            users = users.filter(location__icontains=location)
        
        # Filter by minimum rating
        if min_rating:
            users = users.annotate(
                avg_rating=Avg('ratings_received__rating')
            ).filter(avg_rating__gte=float(min_rating))
        
        users = users.distinct()
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)


class UserStatsView(APIView):
    """View for getting user statistics"""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
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
        
        stats = {
            'total_skills': user.user_skills.count(),
            'teachable_skills': user.user_skills.filter(can_teach=True).count(),
            'skills_wanted': user.skills_wanted.count(),
            'average_rating': user.ratings_received.aggregate(
                Avg('rating')
            )['rating__avg'],
            'total_ratings': user.ratings_received.count(),
            'ratings_given': user.ratings_given.count(),
        }
        
        return Response(stats)