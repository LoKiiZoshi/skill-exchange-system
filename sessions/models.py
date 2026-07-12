from django.db import models

# Create your models here.


from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class SkiSession(models.Model):
    """Represents a ski/snowboard session booked or logged on skiExchange.
    can be a rental session, coaching session, or a guided ski trip"""
    
    SESSION_TYPE_CHOICES = [
        ('rental','Gear Rental'),
        ('coaching','Coaching/ Lesson'), 
        ('guided','Guided Trip'),
        ('freeride','Freeride/Open Session'),
    ]
    
    
    SESSION_TYPE_CHOICES = [
        ('rental','Gear Rental'),
        ('coaching','Coachin/Lesson'),
        ('guided','Guided Trip'),
        ('freeride','Freeride / Open Session'),
        
    ]
    
    
    SESSION_CHOICES = [
        ('pending','Pending'),
        ('confirmed','Confirmed'),
        ('ongoing','Ongoing'),
        ('completed','completed'),
        ('cancelled','Cancelled'),
    ]
    
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate','Intermediate'),
        ('advanced','Advanced'),
        ('expert','Expert'),
        
    ]
    
    # participants 
    
    host = models.ForeignKey(User, on_delete=models.CASCADE,related_name='hosted_sessions',help_text="The instructor, gide, or gear owner")
    participant = models.ForeignKey(User,on_delete=models.CASCADE,related_name='booked_session',help_text="The person who booked the session")
    
    # Session details
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES,default='rental')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES,default='beginne')
    # Linked listing (optional - e.g. gear listing being rented)
    listing_id = models.PositiveBigIntegerField(null=True,blank=True,help_text="ID of the listing (if applicable)")
    listing_title = models.CharField(max_length=255, blank=True)
    
    # Location 
    location = models.CharField(max_length=255, blank=True,help_text="Resort or meting point")
    latitude        = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude       = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
 
    # Scheduling
    start_time      = models.DateTimeField()
    end_time        = models.DateTimeField()
    duration_hours  = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                          validators=[MinValueValidator(0.5)],
                                          help_text="Auto-calculated or manually set duration in hours")
 
    # Pricing
    price_per_hour  = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_price     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
 
    # Status
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cancellation_reason = models.TextField(blank=True)
 
    # Notes
    host_notes      = models.TextField(blank=True, help_text="Private notes by the host")
    participant_notes = models.TextField(blank=True, help_text="Notes or requests by participant")
 
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Ski Session'
        verbose_name_plural = 'Ski Sessions'
 
    def __str__(self):
        return f"{self.title} | {self.host.username} → {self.participant.username} [{self.status}]"
 
    def save(self, *args, **kwargs):
        # Auto-calculate duration in hours if start and end time are set
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_hours = round(delta.total_seconds() / 3600, 2)
        # Auto-calculate total price
        if self.price_per_hour and self.duration_hours:
            self.total_price = round(float(self.price_per_hour) * float(self.duration_hours), 2)
        super().save(*args, **kwargs)
        


class SessionMessage(models.Model):
  """Simple messagin thread attached to a skiSession so host and participant can communicate."""
  
  session = models.ForeignKey(SkiSession, on_delete=models.CASCADE, related_name='messages')
  sender = models.ForeignKey(User, on_delete= models.CASCADE,related_name='session_messages')
  body = models.TextField()
  is_read = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
      ordering = ['created_at']
      verbose_name = 'Session Message'
      verbose_name_plural = 'Session Messages'
      
      def __str__(self):
         return f"[{self.session.title}] {self.sender.username}: {self.body[:50]}"
     