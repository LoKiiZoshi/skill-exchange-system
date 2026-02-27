from django.shortcuts import render

# Create your views here.



from rest_framework import viewsets, status,filters ,generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q, Count , Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend


from .models import(
    ExchangeRequest, ExchangeSession, SessionFeedback,
    SkillExchangeOffer , Booking , Notification
)

from.serializers import(
    ExchangeRequestSerializer, ExchangeRequestUpdateSerializer,
    ExchangeSessionSerializer , ExchangeSessionDetailSerializer,
    SessionFeedbackSerializer , SkillExchangeOfferDetailSerializer,
    SkillExchangeOfferDetailSerializer, BookingSerializer,
    BookingUpdateSerializer, NotificationSerializer
)


User  = get_user_model()

class ExchangeRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for exchange requests"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'skill_offered', 'skill_requested']
    ordering_fields = ['created_at', 'proposed_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update', 'respond']:
            return ExchangeRequestUpdateSerializer
        return ExchangeRequestSerializer

    def get_queryset(self):
        """Return requests sent or received by the current user"""
        user = self.request.user
        return ExchangeRequest.objects.filter(
            Q(requester=user) | Q(receiver=user)
        )
