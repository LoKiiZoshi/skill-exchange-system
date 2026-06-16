from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import(
    UserProfile, Education, Experience,
    Certification,Project,Achievement,ProfileView,Follow,Block
    ,ProfileReport,SocialLink
)

from .serializers import(
    UserProfileSerializer, EducationSerializer, ExperienceSerializer,
    CertificationSerializer, ProjectSerializer as ProjectSerializer, AchievementSerializer, ProfileViewSerializer, FollowSerializer,
    
)



#Helpers

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission: owner can edit, others read read-only."""
    def has_object_permission(self, request,view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj,'user',getattr(obj,'follower',None))
        return owner == request.user


class UserProfileViewSet(viewsets.ModelViewSet):
   
    serializer_class    = UserProfileSerializer
    permission_classes  = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
 
    def get_queryset(self):
        return UserProfile.objects.select_related('user').all()
 
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Record a profile view (anonymous or authenticated)
        if request.user != instance.user:
            ProfileView.objects.create(
                profile    = instance.user,
                viewer     = request.user if request.user.is_authenticated else None,
                ip_address = request.META.get('REMOTE_ADDR'),
                user_agent = request.META.get('HTTP_USER_AGENT', ''),
            )
            instance.profile_views += 1
            instance.save(update_fields=['profile_views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
 
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retrieve or update the current user's own profile."""
        profile = get_object_or_404(UserProfile, user=request.user)
        if request.method == 'GET':
            return Response(self.get_serializer(profile).data)
        serializer = self.get_serializer(profile, data=request.data, partial=request.method == 'PATCH')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
 
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def verify(self, request, pk=None):
        """Mark a profile as verified (staff/admin only)."""
        if not request.user.is_staff:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        profile = self.get_object()
        profile.is_verified = True
        profile.verified_at = timezone.now()
        profile.save(update_fields=['is_verified', 'verified_at'])
        return Response({'status': 'Profile verified.'})
 
 
 
class EducationViewSet(viewsets.ModelViewSet):
    
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Education.objects.filter(User =self.request).order_by('-start_date')
    def perform_create(self, serializer):
        serializer.save(user = self.request.user)
        
        
        
# Experience Viewset

class ExperienceViewSet(viewsets.ModelViewSet):
    
    
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Experience.objects.filter(user = self.request.user).order_by('-start_date')
    
    def perform_create(self, serializer):
        serializer.save(user = self.request.user)
        
        
class CertificationViewSet(viewsets.ModelViewSet):
  
    serializer_class   = CertificationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
 
    def get_queryset(self):
        return Certification.objects.filter(user=self.request.user).order_by('-issue_date')
 
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)





 
# ──────────────────────────────────────────────────────────────
# Project ViewSet
# ──────────────────────────────────────────────────────────────
class ProjectViewSet(viewsets.ModelViewSet):
  

    serializer_class   = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
 
    def get_queryset(self):
        return Project.objects.select_related('user').prefetch_related('technologies').all()
 
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save(update_fields=['views'])
        return Response(self.get_serializer(instance).data)
 
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
 
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        project = self.get_object()
        project.likes += 1
        project.save(update_fields=['likes'])
        return Response({'likes': project.likes})
 
    @action(detail=False, methods=['get'])
    def featured(self, request):
        qs = self.get_queryset().filter(is_featured=True)
        return Response(self.get_serializer(qs, many=True).data)
 
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mine(self, request):
        qs = self.get_queryset().filter(user=request.user)
        return Response(self.get_serializer(qs, many=True).data)