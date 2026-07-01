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
    
    
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('reviewer','reviewed_user').all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter,filters.SearchFilter]
    filterset_fields = ['rating','listing_id','reviewed_user']
    ordering_fields = ['created_at','rating']
    ordering = ['-created_at']
    search_fields = ['tittle', ' body','listing_title']
    
@action(detail=False, methods=['get'], url_path='my_reviews')
def my_reviews(self, request):
        """All reviews written by the authenticated user."""
        qs = self.get_queryset().filter(reviewer=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
    
    
    