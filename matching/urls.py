from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MatchPreferenceViewSet, SkillMatchViewSet, MatchSuggestionViewSet,
    SavedMatchViewSet, MatchFilterViewSet, MatchFeedbackViewSet,
    FindMatchesView, GenerateMatchesView, MatchStatisticsView
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'preferences', MatchPreferenceViewSet, basename='match-preference')
router.register(r'matches', SkillMatchViewSet, basename='skill-match')
router.register(r'suggestions', MatchSuggestionViewSet, basename='match-suggestion')
router.register(r'saved', SavedMatchViewSet, basename='saved-match')
router.register(r'filters', MatchFilterViewSet, basename='match-filter')
router.register(r'feedback', MatchFeedbackViewSet, basename='match-feedback')

app_name = 'matching'

urlpatterns = [
    # Custom endpoints
    path('find/', FindMatchesView.as_view(), name='find-matches'),
    path('generate/', GenerateMatchesView.as_view(), name='generate-matches'),
    path('statistics/', MatchStatisticsView.as_view(), name='match-statistics'),
    
    # Router URLs
    path('', include(router.urls)),
]