from django.urls import path, include
from rest_framework.routers import DefaultRouter
 
from .views import (
    UserProfileViewSet,
    EducationViewSet,
    ExperienceViewSet,
    CertificationViewSet,
    ProjectViewSet,
    AchievementViewSet,
    ProfileViewViewSet,
    FollowViewSet,
)
 
router = DefaultRouter()