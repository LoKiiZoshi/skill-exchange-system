from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


User = get_user_model()

class ExchangeRequest(models.Model):
    """Request to exchange skills between two users"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled','Completed'),
        
    ]
    
    requester = models.ForeignKey(User,on_delete=models.CASCADE,related_name='exchange_requests_sent')
    receiver = models.ForeignKey(User,on_delete= models.CASCADE, related_name='exchange_requests_received')
    
    
    # Skills involved in the exchange
    
    skill_offered = models.ForeignKey('accounts.Skill',on_delete=models.CASCADE,related_name='offered_in_exchanges',help_text="Skill that requester want to teach")
    skill_requested = models.ForeignKey('accounts.Skill', on_delete=models.CASCADE, related_name='requested_in_exchanges',help_text="skill that requester wants to learn")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='pending')
    message = models.TextField(help_text="Message from requester")
    response_message = models.TextField(blank=True, help_text="Response form receiver")
    
    # Proposed schedule
    proposed_date = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=60,validators=[MinValueValidator(15), MaxValueValidator(480)])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True,blank=True)
    
    
    def __str__(self):
        return f"{self.requester.email}_ {self.receiver}: {self.skill_requested.name} for {self.skill_offered.name}"
    
    class Meta:
        ordering = ['-created_at']
        
        
        
    class ExchangeSession(models.Model):
        """Actual skill exchange session between users"""
        
        STATUS_CHOICES = [
            ('scheduled', 'Scheduled'),
            ('in_progress','In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'Now Show')
        ]
        
        
        MEETING_TYPE_CHOICES = [ 
                                ('online', 'Online'),
                                ('in_person', 'In Person'),
                                ('hybrid','Hybrid'),
                                ]