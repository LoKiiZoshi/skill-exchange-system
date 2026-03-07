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

    def _create_session_from_request(self, exchange_request):
        """Create a session from an accepted exchange request"""
        if exchange_request.proposed_date:
            scheduled_start = exchange_request.proposed_date
            scheduled_end = scheduled_start + timezone.timedelta(
                minutes=exchange_request.duration_minutes
            )
            
            ExchangeSession.objects.create(
                exchange_request=exchange_request,
                participant_1=exchange_request.requester,
                participant_2=exchange_request.receiver,
                title=f"{exchange_request.skill_requested.name} ↔ {exchange_request.skill_offered.name}",
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end
            )

    def _create_notification(self, exchange_request):
        """Create notification for exchange request response"""
        notification_type = 'request_accepted' if exchange_request.status == 'accepted' else 'request_rejected'
        
        Notification.objects.create(
            user=exchange_request.requester,
            notification_type=notification_type,
            title=f"Exchange Request {exchange_request.status.title()}",
            message=f"Your exchange request has been {exchange_request.status}.",
            exchange_request=exchange_request
        )


class ExchangeSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for exchange sessions"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'meeting_type']
    ordering_fields = ['scheduled_start', 'created_at']
    ordering = ['-scheduled_start']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExchangeSessionDetailSerializer
        return ExchangeSessionSerializer

    def get_queryset(self):
        """Return sessions where user is a participant"""
        user = self.request.user
        return ExchangeSession.objects.filter(
            Q(participant_1=user) | Q(participant_2=user)
        )

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming sessions"""
        sessions = self.get_queryset().filter(
            scheduled_start__gte=timezone.now(),
            status='scheduled'
        )
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        """Get past sessions"""
        sessions = self.get_queryset().filter(
            scheduled_start__lt=timezone.now()
        ).exclude(status='scheduled')
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a session"""
        session = self.get_object()
        
        if session.status != 'scheduled':
            return Response(
                {'error': 'Only scheduled sessions can be started.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'in_progress'
        session.actual_start = timezone.now()
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a session"""
        session = self.get_object()
        
        if session.status not in ['scheduled', 'in_progress']:
            return Response(
                {'error': 'Invalid session status for completion.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'completed'
        session.actual_end = timezone.now()
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a session"""
        session = self.get_object()
        
        if session.status == 'completed':
            return Response(
                {'error': 'Cannot cancel a completed session.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'cancelled'
        session.save()
        
        # Create notification for other participant
        other_participant = (
            session.participant_2 if session.participant_1 == request.user
            else session.participant_1
        )
        
        Notification.objects.create(
            user=other_participant,
            notification_type='session_cancelled',
            title='Session Cancelled',
            message=f'The session "{session.title}" has been cancelled.',
            session=session
        )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    
class SessionFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for session feedback"""
    serializer_class = SessionFeedbackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['session', 'overall_rating']
    ordering_fields = ['created_at', 'overall_rating']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return feedback for sessions user participated in"""
        user = self.request.user
        return SessionFeedback.objects.filter(
            Q(session__participant_1=user) | Q(session__participant_2=user)
        )

    @action(detail=False, methods=['get'])
    def my_feedback(self, request):
        """Get feedback given by current user"""
        feedbacks = SessionFeedback.objects.filter(user=request.user)
        serializer = self.get_serializer(feedbacks, many=True)
        return Response(serializer.data)



class SkillExchangeOfferViewSet(viewsets.ModelViewSet):
    """ViewSet for skill exchange offers"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'skill', 'availability', 'requires_exchange']
    search_fields = ['title', 'description', 'skill__name']
    ordering_fields = ['created_at', 'total_sessions', 'total_students']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SkillExchangeOfferDetailSerializer
        return SkillExchangeOfferSerializer

    def get_queryset(self):
        """Return all active offers or user's own offers"""
        user = self.request.user
        
        # Show user's own offers regardless of status
        user_offers = Q(user=user)
        # Show active offers from other users
        active_offers = Q(status='active') & ~Q(user=user)
        
        return SkillExchangeOffer.objects.filter(user_offers | active_offers)

    @action(detail=False, methods=['get'])
    def my_offers(self, request):
        """Get current user's offers"""
        offers = SkillExchangeOffer.objects.filter(user=request.user)
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active offers"""
        offers = SkillExchangeOffer.objects.filter(status='active').exclude(user=request.user)
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle offer status between active and paused"""
        offer = self.get_object()
        
        # Only owner can toggle status
        if offer.user != request.user:
            return Response(
                {'error': 'Only the offer owner can toggle status.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if offer.status == 'active':
            offer.status = 'paused'
        elif offer.status == 'paused':
            offer.status = 'active'
        else:
            return Response(
                {'error': 'Cannot toggle status of closed offers.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offer.save()
        serializer = self.get_serializer(offer)
        return Response(serializer.data)
