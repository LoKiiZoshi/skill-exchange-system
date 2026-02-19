from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, UserProfileView, UserDetailView,
    ChangePasswordView, SkillCategoryViewSet, SkillViewSet,
    UserSkillViewSet, SkillWantedViewSet, UserRatingViewSet,
    SearchUsersView, UserStatsView
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'categories', SkillCategoryViewSet, basename='skill-category')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'user-skills', UserSkillViewSet, basename='user-skill')
router.register(r'skills-wanted', SkillWantedViewSet, basename='skill-wanted')
router.register(r'ratings', UserRatingViewSet, basename='user-rating')

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Search and stats endpoints
    path('search/', SearchUsersView.as_view(), name='search-users'),
    path('stats/', UserStatsView.as_view(), name='user-stats'),
    path('stats/<int:user_id>/', UserStatsView.as_view(), name='user-stats-detail'),
    
    # Router URLs
    path('', include(router.urls)),
]