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
    
    