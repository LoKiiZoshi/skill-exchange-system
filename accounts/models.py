from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator,MaxValueValidator

class User(AbstractUser):
    """Extended User model for Skill Exchange Platform"""
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500,blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True,null=True)
    location = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15,blank=True)
    date_of_birth = models.DateField(null=True,blank=True)
    is_email_verified = models.BooleanField(auto_created=True)
    updated_at = models.DateTimeField(auto_now = True)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']
    
    
    def __str__(self):
        return f"{self.email} - {self.get_full_name()}"
    
    
    class Meta:
        ordering = ['-created_at']
        
        
class SkillCategory(models.Model):
    """Categories for skills(e.g. , Programming , Design, Language, etc , etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank = True)
    icon = models.CharField(max_length=50, blank=True)  # for storing icon class
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_Plural = "Skill Categories"
        ordering = ['name']
        
        
class Skill(models.Model):
    """Individual skill that users can offer or or want to learn"""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(SkillCategory,on_delete=models.CASCADE,related_name='skills')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name}({self.category.name})"
    
    class Meta:
        ordering = ['category','name']
        unique_together = ['name','category']
        
        
class UserSkill(models.Model):
    """Skills that a user posesses with with profieciency level"""
    PROFICIENCY_LEVELS = [
        ('beginner', 'Beginnner'),
        ('intermediate','Intermediate'),
        ('advanced','Advanced'),
        ('expert','Expert'),
    ]
    
    
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user_skillls')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE,related_name='user_skills')
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    years_of_experience = models.PositiveIntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(50)])
    
    can_teach = models.BooleanField(default=True)
    description = models.TextField(blank= True, help_text="Describe your experience with this skill")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.user.email} - {self.skill.name} ({self.proficiency_level})"

