from django.db import models
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
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exchange_requests_sent'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exchange_requests_received'
    )
    
    # Skills involved in the exchange
    skill_offered = models.ForeignKey(
        'accounts.Skill',
        on_delete=models.CASCADE,
        related_name='offered_in_exchanges',
        help_text="Skill that requester wants to teach"
    )
    skill_requested = models.ForeignKey(
        'accounts.Skill',
        on_delete=models.CASCADE,
        related_name='requested_in_exchanges',
        help_text="Skill that requester wants to learn"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(help_text="Message from requester")
    response_message = models.TextField(blank=True, help_text="Response from receiver")
    
    # Proposed schedule
    proposed_date = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(15), MaxValueValidator(480)]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.requester.email} → {self.receiver.email}: {self.skill_requested.name} for {self.skill_offered.name}"

    class Meta:
        ordering = ['-created_at']


class ExchangeSession(models.Model):
    """Actual skill exchange session between users"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    MEETING_TYPE_CHOICES = [
        ('online', 'Online'),
        ('in_person', 'In Person'),
        ('hybrid', 'Hybrid'),
    ]

    exchange_request = models.ForeignKey(
        ExchangeRequest,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    participant_1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions_as_participant_1'
    )
    participant_2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions_as_participant_2'
    )
    
    # Session details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='online')
    
    # Schedule
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Location/Meeting info
    meeting_link = models.URLField(blank=True, help_text="Online meeting link")
    location = models.CharField(max_length=200, blank=True, help_text="Physical location if in-person")
    
    # Notes
    notes = models.TextField(blank=True)
    participant_1_notes = models.TextField(blank=True)
    participant_2_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.scheduled_start.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-scheduled_start']

    @property
    def duration_minutes(self):
        """Calculate duration in minutes"""
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return int(delta.total_seconds() / 60)
        delta = self.scheduled_end - self.scheduled_start
        return int(delta.total_seconds() / 60)


class SessionFeedback(models.Model):
    """Feedback for a completed session"""
    session = models.ForeignKey(
        ExchangeSession,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='session_feedbacks_given'
    )
    
    # Ratings
    overall_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    teaching_quality = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    communication = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    punctuality = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Feedback
    what_went_well = models.TextField(blank=True)
    what_to_improve = models.TextField(blank=True)
    additional_comments = models.TextField(blank=True)
    
    # Would recommend
    would_recommend = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Feedback by {self.user.email} for {self.session.title}"

    class Meta:
        unique_together = ['session', 'user']
        ordering = ['-created_at']


class SkillExchangeOffer(models.Model):
    """Public offer to teach a skill"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
    ]

    AVAILABILITY_CHOICES = [
        ('weekdays', 'Weekdays'),
        ('weekends', 'Weekends'),
        ('flexible', 'Flexible'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='skill_offers'
    )
    skill = models.ForeignKey(
        'accounts.Skill',
        on_delete=models.CASCADE,
        related_name='teaching_offers'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="What you will teach")
    prerequisites = models.TextField(blank=True, help_text="What students should know")
    
    # Offering details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    max_students = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    session_duration = models.PositiveIntegerField(
        default=60,
        help_text="Session duration in minutes"
    )
    
    # Availability
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='flexible')
    preferred_meeting_type = models.CharField(
        max_length=20,
        choices=ExchangeSession.MEETING_TYPE_CHOICES,
        default='online'
    )
    
    # Exchange preference
    requires_exchange = models.BooleanField(
        default=True,
        help_text="Whether you want a skill in exchange"
    )
    desired_skills = models.ManyToManyField(
        'accounts.Skill',
        related_name='desired_by_offers',
        blank=True,
        help_text="Skills you want to learn in exchange"
    )
    
    # Stats
    total_sessions = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} offers {self.skill.name}"

    class Meta:
        ordering = ['-created_at']


class Booking(models.Model):
    """Booking for a skill exchange offer"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    offer = models.ForeignKey(
        SkillExchangeOffer,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings_made'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(help_text="Message from student")
    
    # Proposed time
    proposed_datetime = models.DateTimeField()
    
    # Skills offered in exchange (if applicable)
    exchange_skill = models.ForeignKey(
        'accounts.Skill',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offered_in_bookings'
    )
    exchange_message = models.TextField(blank=True)
    
    # Session (created after confirmation)
    session = models.OneToOneField(
        ExchangeSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booking'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.email} → {self.offer.title}"

    class Meta:
        ordering = ['-created_at']


class Notification(models.Model):
    """Notification system for users"""
    NOTIFICATION_TYPES = [
        ('exchange_request', 'Exchange Request'),
        ('request_accepted', 'Request Accepted'),
        ('request_rejected', 'Request Rejected'),
        ('session_reminder', 'Session Reminder'),
        ('session_cancelled', 'Session Cancelled'),
        ('feedback_received', 'Feedback Received'),
        ('booking_request', 'Booking Request'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('new_message', 'New Message'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    exchange_request = models.ForeignKey(
        ExchangeRequest,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    session = models.ForeignKey(
        ExchangeSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    class Meta:
        ordering = ['-created_at']

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()