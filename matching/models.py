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
 
 
 
class SkillMatch(models.Model):
    """Potential skill matches between users"""
    MATCH_TYPE_CHOICES = [
        ('mutual_exchange','Mutual Exchange'),
        ('one_way_teaching','One way Teaching'),
        ('group_learning','Group Learning'),
        
    ]
    
    user1 = models.ForeignKey(User,on_delete=models.CASCADE,related_name='matches_as_user2')
    
    # Skill involved
    user1_skill = models.ForeignKey('account.Skill',on_delete=models.CASCADE,related_name='matches_as_user1_skill',help_text = "Skill that user1 can teach")
    
    user2_skill = models.ForeignKey('accounts.Skill', on_delete=models.CASCADE,related_name='matches_as_user2_skill',null=True,blank=True,help_text="Skill that user2 can teach") 
    
    # Match details
    match_type = models.CharField(max_length=30, choices=MATCH_TYPE_CHOICES)
    match_score = models.DecimalField(max_digits=5, decimal_places=2,validators=[MinValueValidator(0.0),MaxValueValidator(100.0)],help_text="Match compatibility score (0-100)")
    
    # Match factors
    skill_compatibility = models.DecimalField(max_digits=5,decimal_places=2,default=0.0)
    location_compatibility = models.DecimalField(max_digits=5,decimal_places=2,default=0.0)
    availability_compatibility = models.DecimalField(max_digits=5 ,decimal_places=2, default=0.0)
    experience_compatibility = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    rating_compatibility = models.DecimalField(max_digits=5, decimal_places=2,default=0.0)
    
    # Status 
    is_active = models.BooleanField(default=True)
    viewed_by_user1 = models.BooleanField(default=False)
    viewed_by_user2 = models.BooleanField(default=False)
    
    
    # Interaction tracking 
    user1_interested = models.BooleanField(default=False)
    user2_interested = models.BooleanField(default=False)
    exchange_request_created = models.BooleanField(default=False)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.user1.email}-{self.user2.email}({self.match_score}%)"
    
    class Meta:
        ordering = ['-match_score', '-create_at']
        unique_together = ['user1','user2','user1_skill']
        indexes = [
            models.Index(fields=['-match_score']),
            models.Index(fields=['user1','-match_score']),
            models.Index(fields=['user2','-match_score']),
        ]
 
    
class MatchSuggestion(models.Model):
    """AI - powered match suggestions"""
    SUGGESTION_TYPE_CHOICES = [
        ('perfect_match','Perfect Match'),
        ('good_match','Good Match'),
        ('potential_match','Potential Match'),
        ('skill_complement', 'Skill Complement'),
        ('similar_interest', 'Similar Interest'),
        
    ]
    
    
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='match_suggestions')
    suggested_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='suggested_to')
    suggestion_type = models.CharField(max_length=30, choices=SUGGESTION_TYPE_CHOICES)
    reason = models.TextField(help_text="Why this user is suggested")
    
    
    # Skills involved
    
    primary_skill = models.ForeignKey('accounts.Skill', on_delete=models.CASCADE,related_name='primary_in_suggestions',null=True,blank=True)
    # Suggestion score
    suggestion_score = models.DecimalField(max_digits=5,decimal_places=2,validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])


# User interaction
viewwed = models.BooleanField(default=False)
viewwed_at = models.DateTimeField(null=True, blank=True)
dismissed = models.BooleanField(default=False)
dismissed_at = models.DateTimeField(null=True, blank=True)
accepted = models.BooleanField(default=False)
accepted_at = models.DateTimeField(null=True, blank=True)


created_at = models.DateTimeField(auto_now_add=True)
expires_at = models.DateTimeField(help_text="When this suggestion expires",
                                  null=True,
                                  blank=True)
def __str__(self):
    return f"Suggest {self.suggested_user.email}to{self.user.email}"

class Meta:
    ordering = ['-suggestion_score','-created_At']
    indexes = [
        models.Index(fields =['user','-suggestion_score']),
        models.Index(fields=['user', 'dismissed','viewed']),
        
    ]
    
    
    def mark_as_viewed(self):
        """Mark suggestion as viewed"""
        if not self.viewed:
            self.viewed = True
            self.viewed_at = timezone.now()
            self.save()
            
            
    def dismiss(self):
        """Dismiss this suggestion"""
        self.dismissed = True
        self.dismissed_at = timezone.now()
        self.save()
        
    def accept(self):
        """Accept this suggestion"""
        self.accepted = True
        self.accepted_at = timezone.now()
        self.save()    
        
        
    class SavedMatch(models.Model):
        """Matches saved/bookmarked by users"""
        user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='saved_matches')
        matched_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='saved_by')
        skill_match = models.ForeignKey(SkillMatch,on_delete=models.CASCADE,related_name='saved_by_users',null=True,blank=True)
        notes = models.TextField(blank=True,help_text="Personal notes about this match")
        created_at = models.DateTimeField(auto_now_add=True)
        
        
        def __str__(self):
            return f"{slef.user.email}saved{self.matched_user.email}"
        
        class Meta:
            Unique_together = ['User','matched_user']
            ordering = ['-created_at']
            
            
            
class MatchFilter(models.Model):
    """Custom filter created by users for finding matches"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='match_filters')
    name = models.CharField(max_length=100, help_text="Filter name")
    description = models.TextField(blank=True)
    
    # Filter criteria
    skill_categories = models.ManyToManyField('accounts.SkillCategory',blank=True,related_name='used_in_filters')
    skills = models.ManyToManyField('accounts.Skill',blank=True,related_name='used_in_filters')
    
    min_rating = models.DecimalField(max_digits=3, decimal_places=3,null=True,blank=True,validators=[MinValueValidator(0.0),MaxValueValidator(5.0)])
    min_experience = models.PositiveBigIntegerField(null=True,blank=True)
    location = models.CharField(max_length=200,blank=True)
    max_distance = models.CharField(max_length=20,blank=True)
    meeting_type = models.CharField(max_length=20,blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']
        
        
class MatchAnalytics(models.Model):
    """Anaytics for match quality and outcomes"""
    skill_match = models.OneToOneField(SkillMatch,on_delete=models.CASCADE,related_name='analytics')
    
    # Interaction metrics
    total_views = models.PositiveBigIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)
    exchange_request_sent = models.BooleanField(default=False)
    exchange_completed = models.BooleanField(default=False)
    
    # Quality metrics
    user1_satisfaction = models.PositiveIntegerField(null=True,blank=True,validators=[MinValueValidator(1),MaxValueValidator(5)])
    user2_satisfaction = models.PositiveIntegerField(null=True,blank=True,validators=[MinValueValidator(1),MaxValueValidator(5)])
    
    # Outcome
    sucessful_match = models.BooleanField(default=False)
    match_quality_score = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for Match {self.skill_match}"
    
    class Meta:
        verbose_name = "Match Analytics"
        verbose_name_plural = "Match Analytics"
        
        
class MatchFeedback(models.Model):
    """Feedback on match quality"""
    FEEDBACK_TYPE_CHOICES = [
        ('helpful','Helpful Match'),
        ('not_helpful','Not Helpful')
        ('incorrect','Incorrect Match'),
        ('spam', 'Spam/Inapproprite'),
        
    ]
    
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='match_feedbacks')
    skill_match = models.ForeignKey(SkillMatch, on_delete=models.CASCADE,related_name='feedbacks')
    
    feedback_type = models.CharField(max_length=20,choices = FEEDBACK_TYPE_CHOICES)
    reating = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)],)
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.feedback_type}"
    
    class Meta:
        Unique_together = ['user','skill_match']
        ordering = ['-created_at']
        
        