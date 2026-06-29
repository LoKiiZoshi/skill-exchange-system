from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    RATIN_CHOICES = [(i,str(i) in range(1, 6)))]
    
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE,related_name='reviews_given')
    reviewed_user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True,related_name='reviews_received')
    # Ger /listing being reviewed (nullable so user-only reviews also work)
listing_id = models.PositiveBigIntegerField(null=True,blank=True,help_text="Id of the ski gear listing being reviewed")
listing_tittle = models.CharField(max_length=255, blank=True,help_text="Snapshot of the listing title at review time")
rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)],help_text="Rating from 1 (worst) to 5 (best)")
title = models.CharField(max_length=200,blank=True)
body = models.TextField()
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)


class Meta:
    ordering = ['-created at']
    # A user can review the same listing or seller only once 
    unique_together = [('reviewer','listing_id'),('reviewer','reviewed_user')]
    verbose_name = 'Review'
    verbose_name_plural = 'Reviews'
    
    def __str__(self):
         target = self.listing_title or (str(self.reviewed_user) if self.reviewed_user else 'Unknow')
         return f"{self.reviewer.username} - {target} ({self.rating})" 