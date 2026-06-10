from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import(
    UserProfile, Education, Experience,Certification,Project,Achievement,ProfileView,Follow,Block
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
