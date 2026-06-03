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
    
    
    
    
# Education     

class Education(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE,related_name='education')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    fields_of_study = models.CharField(max_length=255,blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True,blank=True)
    is_current = models.BooleanField(null=True,blank=True)   
    grade = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        
        
    def __str__(self):
        return f"{self.degree} at {self.institution}"
    
    
    
    
    
# Experience 

class Experience(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full TIme'),
        ('part_time','Part Time'),
        ('contract', 'Contract'),
        ('internship','Internship'),
        ('freelance', 'Freelance'),
        ('self_employed','self Employed'),
        ('volunter', 'Volunteer'),
    ]
        
        
user = models.ForeignKey(User, on_delete = models.CASCADE, related_name='experiences')
title = models.CharField(max_length=255)
company = models.CharField(max_length=255)
employment_type = models.CharField(max_length=20,choices=EMPLOYMENT_TYPE_CHOICES,blank=True)
location = models.CharField(max_length=255,blank=True)
start_date = models.DateField()
end_date = models.DateField(null=True,blank=True)
is_current = models.BooleanField(default=True)
description = models.TextField(balnk = True)

create_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)

class Meta:
    ordering = ['-start_date']
    
def __str__(self):
    return f"{self.title}at {self.company}"



# Certification

class Certification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cerfications')
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    credential_id = models.CharField(max_length=255, blank=True)
    credential_url = models.URLField(blank=True)
    issue_date = models.DateField()
    expiration_date = models.DateField(null= True, blank=True)
    does_not_expire = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        ordering = [' -issue_date']

    @property
    def is_expired(self):
        if self.does_not_expire or not self.expiration_date:
            return False
        
        return self.expiration_date < timezone.now().date()
    
    def __str__(self):
        return f"{self.name} - {self.issuing_organization}"
    
    
    
class Project(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed',   'Completed'),
        ('on_hold',     'On Hold'),
        ('abandoned',   'Abandoned'),
    ]
 
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title            = models.CharField(max_length=255)
    description      = models.TextField(blank=True)
    project_url      = models.URLField(blank=True)
    repository_url   = models.URLField(blank=True)
    start_date       = models.DateField(null=True, blank=True)
    end_date         = models.DateField(null=True, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    # Technologies is a ManyToMany to a Skill model (from accounts app)
    technologies     = models.ManyToManyField('accounts.Skill', blank=True, related_name='projects')
    thumbnail        = models.ImageField(upload_to='project_thumbnails/', null=True, blank=True)
    views            = models.PositiveIntegerField(default=0)
    likes            = models.PositiveIntegerField(default=0)
    is_featured      = models.BooleanField(default=False)
 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ['-created_at']
 
    def __str__(self):
        return self.title
    
    
    
    
# ──────────────────────────────────────────────
# Achievement
# ──────────────────────────────────────────────
class Achievement(models.Model):
    ACHIEVEMENT_TYPE_CHOICES = [
        ('skill',       'Skill'),
        ('session',     'Session'),
        ('connection',  'Connection'),
        ('project',     'Project'),
        ('streak',      'Streak'),
        ('other',       'Other'),
    ]
 
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES)
    title            = models.CharField(max_length=255)
    description      = models.TextField(blank=True)
    icon             = models.CharField(max_length=100, blank=True)
    badge_image      = models.ImageField(upload_to='badges/', null=True, blank=True)
    target_value     = models.PositiveIntegerField(default=1)
    current_value    = models.PositiveIntegerField(default=0)
    is_unlocked      = models.BooleanField(default=False)
    unlocked_at      = models.DateTimeField(null=True, blank=True)
 
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['-created_at']
 
    def __str__(self):
        return f"{self.title} ({self.user.email})"
 
    def save(self, *args, **kwargs):
        if self.current_value >= self.target_value and not self.is_unlocked:
            self.is_unlocked = True
            self.unlocked_at = timezone.now()
        super().save(*args, **kwargs)
 
  

class ProfileView(models.Model):
    profile    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_views')
    viewer     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_views', null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    viewed_at  = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['-viewed_at']
 
    def __str__(self):
        return f"{self.viewer} viewed {self.profile} at {self.viewed_at}"
    
    
    
    
    
    
class Follow(models.Model):
    follower   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_set')
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']
 
    def __str__(self):
        return f"{self.follower} follows {self.following}"