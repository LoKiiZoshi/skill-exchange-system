from django.shortcuts import render

# Create your views here.   
from django.db.models import Avg, Count
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Review
from .serializers import ReviewSerializer


class IsReviewerOrReadOnly(permissions.BasePermission):
    """Allow only the review's author to edit or delete it."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFF_METHODS:
            return True
        return obj.reviewer == request.User
    
    
    

