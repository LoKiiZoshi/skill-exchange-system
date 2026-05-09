from django.db import models

# Create your models here.


from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# User profile 


class UserProfile(models.Model):
    VISIBILITY_CHOICES = [
        ('public','Public'),
        ('private','Private'),
        ('friends','Friends Only'),
    ]
    
    user = models.OneToOneField(
        user, on_delete=models.CASCADE,related_name = 'profile'
    )
    
    
    
    #Bio / links
    
    headline = models.CharField(max_length=255,blank=True)
    about = models.TextField(blank=True)
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Privacy
    show_email = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)
    show_location = models.BooleanField(default=True)
    profile_visibility = models.CharField(max_length=10,choices=VISIBILITY_CHOICES, default='public')
    
    # Notifications
    email_notifications = models.BooleanField(default=True)
    match_notifications = models.BooleanField(default=True)
    message_notifications = models.BooleanField(default=True)
    session_reminders = models.BooleanField(default=True)
    
    
    # Stats
    profile_views = models.PositiveBigIntegerField(default=0)
    last_active = models.DateTimeField(null=True, blank=True)
    
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=, blank=True)
    
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        ordering = [-created_at]
        
    def __str__(self):
        return f"Profile of {self.user.email}"