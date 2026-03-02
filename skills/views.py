
Copy

from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    ExchangeRequest, ExchangeSession, SessionFeedback,
    SkillExchangeOffer, Booking, Notification
)
from .serializers import (
    ExchangeRequestSerializer, ExchangeRequestUpdateSerializer,
    ExchangeSessionSerializer, ExchangeSessionDetailSerializer,
    SessionFeedbackSerializer, SkillExchangeOfferSerializer,
    SkillExchangeOfferDetailSerializer, BookingSerializer,
    BookingUpdateSerializer, NotificationSerializer
)

User = get_user_model()


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

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get requests sent by current user"""
        requests = ExchangeRequest.objects.filter(requester=request.user)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def received(self, request):
        """Get requests received by current user"""
        requests = ExchangeRequest.objects.filter(receiver=request.user)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending requests"""
        requests = ExchangeRequest.objects.filter(
            Q(requester=request.user) | Q(receiver=request.user),
            status='pending'
        )
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Respond to an exchange request (accept/reject)"""
        exchange_request = self.get_object()
        
        # Only receiver can respond
        if exchange_request.receiver != request.user:
            return Response(
                {'error': 'Only the receiver can respond to this request.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Can only respond to pending requests
        if exchange_request.status != 'pending':
            return Response(
                {'error': 'This request has already been responded to.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ExchangeRequestUpdateSerializer(
            exchange_request,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # If accepted, create a session
            if serializer.validated_data.get('status') == 'accepted':
                self._create_session_from_request(exchange_request)
            
            # Create notification
            self._create_notification(exchange_request)
            
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)