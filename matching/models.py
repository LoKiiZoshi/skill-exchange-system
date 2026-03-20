from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

class MatchPreference(models.Model):
    """User preferences for matching"""
    DISTANCE_CHOICES = [
        ('any', 'Any Distance'),
        ('5km', 'Within 5 km'),
        ('10km', 'Within 10 km'),
        ('25km', 'Within 25 km'),
        ('50km', 'Within 50 km'),
        ('100km', 'Within 100 km'),
    ]
 
    MEETING_PREFERENCE_CHOICES = [
        ('any', 'Any'),
        ('online_only', 'Online Only'),
        ('in_person_only', 'In Person Only'),
        ('hybrid', 'Hybrid'),
    ]
 
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='match_preference'
    )
    
    # Location preferences
    max_distance = models.CharField(
        max_length=20,
        choices=DISTANCE_CHOICES,
        default='any'
    )
    
    # Meeting preferences
    meeting_preference = models.CharField(
        max_length=20,
        choices=MEETING_PREFERENCE_CHOICES,
        default='any'
    )
    
    # Availability preferences
    available_weekdays = models.BooleanField(default=True)
    available_weekends = models.BooleanField(default=True)
    available_mornings = models.BooleanField(default=True)
    available_afternoons = models.BooleanField(default=True)
    available_evenings = models.BooleanField(default=True)
    
    # Rating preferences
    min_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    
    # Experience preferences
    min_years_experience = models.PositiveIntegerField(default=0)
    
    # Other preferences
    prefer_verified_users = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return f"Match Preferences - {self.user.email}"
 
    class Meta:
        verbose_name = "Match Preference"
        verbose_name_plural = "Match Preferences"
 

