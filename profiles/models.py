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
    
    
    
        