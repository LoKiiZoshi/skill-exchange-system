from django.shortcuts import render

# Create your views here.

from django.db.models import Count,Avg,Q
from django.utils import timezone
from rest_framework import viewsets,permissions,filters,status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import SkiSession, SessionMessage
from .serializers import(
    SkiSessionSerializer, SkiSessionListSerializer,SessionMessageSeriaizer
)


# Permissions
class IsHostOrParticipantOrReadOnly(permissions.BasePermission):
    """Only the host or participant of a session may edit or delete it."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user in (obj.host.participant)
    
class IsMessageSender(permissions.BasePermission):
    """Only the sender of a message may edit or delete it."""
    def hs_object_permission(self,request,view,obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.sender == request.user
    

# SkiSession ViewSet ----
class SkiSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsHostOrParticipantOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter,filters.SearchFilter]
    filterset_fields = ['status','session_type','skill_level','host','participant']
    ordering_fields = ['start_time','created_at','total_price']
    ordering_fields = ['title','description','location','listing_title']
    
    def get_queryset(self):
        return SkiSession.objects.select_related('host','participant').prefetch_related('messages')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SkiSessionListSerializer
        return SkiSessionListSerializer
        return SkiSessionSerializer
    
    # ----- Custom actions --------------------
    
    @action(detail=False,methods=['get'],url_path = 'my_sessions')
    def my_sessions(self,request):
      """"All sessions where the current user is host Or Participant"""
      qs = self.get_queryset().filter(
          Q(host=request.user)|Q(participant = request.user)
          
      )
      
      serializer = SkiSessionListSerializer(qs,many =True,context = {'request':request})
      return Response(serializer.data)
  
  
    @action(detail = False,methods =['get'], url_path = 'upcoming')
    def upcoming(self, request):
        """Confirmed future session for the current user."""
        qs = self.get_queryset().filter(
            Q(host = request.user)|Q(participant = request.user),
            status = 'confirmed',
            start_time__gt = timezone.now(),
            
        )
        serializer = SkiSessionListSerializer(qs, many=True,context = {'request':request})
        return Response(serializer.data)
    
    
    @action(detail=False,methods=['get'],url_path='past')
    def past(self,request):
        """Completed Sessions for the current user."""
        qs = self.get_queryset().filter(
            Q(host = request.user)|Q(participant = request.user),
            status = 'completed',
        )
        
        serializer = SkiSessionListSerializer(qs,many = True,context = {'request':request})
        return Response(serializer.data)
    
    
    
    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm(self, request, pk=None):
        """Host confirms a pending session."""
        session = self.get_object()
        if session.host != request.user:
            return Response({'detail': 'Only the host can confirm a session.'}, status=403)
        if session.status != 'pending':
            return Response({'detail': f'Cannot confirm a session with status "{session.status}".'}, status=400)
        session.status = 'confirmed'
        session.save(update_fields=['status', 'updated_at'])
        return Response({'detail': 'Session confirmed.', 'status': session.status})