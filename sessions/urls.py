from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SkiSessionViewSet,SessionMessageViewSet

router = DefaultRouter()
router.register(r'session', SkiSessionViewSet, basename='session')
router.register(r'session-messages', SessionMessageViewSet,basename='session-message')

urlpatterns = [
    path('',include(router.urls)),
]
