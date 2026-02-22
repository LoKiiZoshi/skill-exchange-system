from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExchangeRequestViewSet, ExchangeSessionViewSet,
    SessionFeedbackViewSet, SkillExchangeOfferViewSet,
    BookingViewSet, NotificationViewSet, DashboardStatsView
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'exchange-requests', ExchangeRequestViewSet, basename='exchange-request')
router.register(r'sessions', ExchangeSessionViewSet, basename='session')
router.register(r'feedback', SessionFeedbackViewSet, basename='feedback')
router.register(r'offers', SkillExchangeOfferViewSet, basename='offer')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'notifications', NotificationViewSet, basename='notification')

app_name = 'skills'

urlpatterns = [
    # Dashboard stats
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Router URLs
    path('', include(router.urls)),
]