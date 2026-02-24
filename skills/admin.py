from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    ExchangeRequest, ExchangeSession, SessionFeedback,
    SkillExchangeOffer, Booking, Notification
)


@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(admin.ModelAdmin):
    """Admin configuration for ExchangeRequest"""
    list_display = [
        'id', 'requester_display', 'receiver_display',
        'skill_offered_display', 'skill_requested_display',
        'status_badge', 'proposed_date', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'proposed_date']
    search_fields = [
        'requester__email', 'requester__username',
        'receiver__email', 'receiver__username',
        'skill_offered__name', 'skill_requested__name',
        'message'
    ]
    readonly_fields = ['created_at', 'updated_at', 'responded_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Participants', {
            'fields': ('requester', 'receiver')
        }),
        ('Skills', {
            'fields': ('skill_offered', 'skill_requested')
        }),
        ('Request Details', {
            'fields': ('status', 'message', 'response_message', 'proposed_date', 'duration_minutes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'responded_at'),
            'classes': ('collapse',)
        }),
    )

    def requester_display(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.requester.id,
            obj.requester.email
        )
    requester_display.short_description = 'Requester'

    def receiver_display(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.receiver.id,
            obj.receiver.email
        )
    receiver_display.short_description = 'Receiver'

    def skill_offered_display(self, obj):
        return obj.skill_offered.name
    skill_offered_display.short_description = 'Skill Offered'

    def skill_requested_display(self, obj):
        return obj.skill_requested.name
    skill_requested_display.short_description = 'Skill Requested'

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'accepted': 'green',
            'rejected': 'red',
            'cancelled': 'gray',
            'completed': 'blue',
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(ExchangeSession)
class ExchangeSessionAdmin(admin.ModelAdmin):
    """Admin configuration for ExchangeSession"""
    list_display = [
        'id', 'title', 'participant_1_display', 'participant_2_display',
        'status_badge', 'meeting_type', 'scheduled_start', 'duration_display'
    ]
    list_filter = ['status', 'meeting_type', 'scheduled_start', 'created_at']
    search_fields = [
        'title', 'description',
        'participant_1__email', 'participant_1__username',
        'participant_2__email', 'participant_2__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-scheduled_start']
    date_hierarchy = 'scheduled_start'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('exchange_request', 'title', 'description', 'status', 'meeting_type')
        }),
        ('Participants', {
            'fields': ('participant_1', 'participant_2')
        }),
        ('Schedule', {
            'fields': ('scheduled_start', 'scheduled_end', 'actual_start', 'actual_end')
        }),
        ('Meeting Details', {
            'fields': ('meeting_link', 'location')
        }),
        ('Notes', {
            'fields': ('notes', 'participant_1_notes', 'participant_2_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def participant_1_display(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.participant_1.id,
            obj.participant_1.get_full_name()
        )
    participant_1_display.short_description = 'Participant 1'

    def participant_2_display(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.participant_2.id,
            obj.participant_2.get_full_name()
        )
    participant_2_display.short_description = 'Participant 2'

    def status_badge(self, obj):
        colors = {
            'scheduled': 'blue',
            'in_progress': 'orange',
            'completed': 'green',
            'cancelled': 'red',
            'no_show': 'gray',
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.status.replace('_', ' ').upper()
        )
    status_badge.short_description = 'Status'

    def duration_display(self, obj):
        return f"{obj.duration_minutes} min"
    duration_display.short_description = 'Duration'


@admin.register(SessionFeedback)
class SessionFeedbackAdmin(admin.ModelAdmin):
    """Admin configuration for SessionFeedback"""
    list_display = [
        'id', 'session_title', 'user_display', 'overall_rating_stars',
        'teaching_quality_stars', 'would_recommend_badge', 'created_at'
    ]
    list_filter = [
        'overall_rating', 'teaching_quality', 'communication',
        'punctuality', 'would_recommend', 'created_at'
    ]
    search_fields = [
        'session__title', 'user__email', 'user__username',
        'what_went_well', 'what_to_improve', 'additional_comments'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('session', 'user')
        }),
        ('Ratings', {
            'fields': ('overall_rating', 'teaching_quality', 'communication', 'punctuality')
        }),
        ('Feedback', {
            'fields': ('what_went_well', 'what_to_improve', 'additional_comments', 'would_recommend')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def session_title(self, obj):
        return obj.session.title
    session_title.short_description = 'Session'

    def user_display(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.get_full_name()
        )
    user_display.short_description = 'User'

    def overall_rating_stars(self, obj):
        return '⭐' * obj.overall_rating
    overall_rating_stars.short_description = 'Overall'

    def teaching_quality_stars(self, obj):
        return '⭐' * obj.teaching_quality
    teaching_quality_stars.short_description = 'Teaching'

    def would_recommend_badge(self, obj):
        if obj.would_recommend:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    would_recommend_badge.short_description = 'Recommend'


@admin.register(SkillExchangeOffer)
class SkillExchangeOfferAdmin(admin.ModelAdmin):
    """Admin configuration for SkillExchangeOffer"""
    list_display = [
        'id', 'title', 'user_display', 'skill_name',
        'status_badge', 'total_sessions', 'total_students',
        'availability', 'created_at'
    ]
    list_filter = [
        'status', 'availability', 'preferred_meeting_type',
        'requires_exchange', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'user__email',
        'user__username', 'skill__name'
    ]
    readonly_fields = ['total_sessions', 'total_students', 'created_at', 'updated_at']
    ordering = ['-created_at']
    filter_horizontal = ['desired_skills']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'skill', 'title', 'description', 'prerequisites', 'status')
        }),
        ('Offering Details', {
            'fields': ('max_students', 'session_duration', 'availability', 'preferred_meeting_type')
        }),
        ('Exchange Details', {
            'fields': ('requires_exchange', 'desired_skills')
        }),
        ('Statistics', {
            'fields': ('total_sessions', 'total_students')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_display(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.get_full_name()
        )
    user_display.short_description = 'Teacher'

    def skill_name(self, obj):
        return obj.skill.name
    skill_name.short_description = 'Skill'

    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'paused': 'orange',
            'closed': 'gray',
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for Booking"""
    list_display = [
        'id', 'offer_title', 'student_display', 'teacher_display',
        'status_badge', 'proposed_datetime', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'proposed_datetime']
    search_fields = [
        'offer__title', 'student__email', 'student__username',
        'offer__user__email', 'message'
    ]
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('offer', 'student', 'status', 'message')
        }),
        ('Schedule', {
            'fields': ('proposed_datetime',)
        }),
        ('Exchange Details', {
            'fields': ('exchange_skill', 'exchange_message')
        }),
        ('Session', {
            'fields': ('session',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at'),
            'classes': ('collapse',)
        }),
    )

    def offer_title(self, obj):
        return obj.offer.title
    offer_title.short_description = 'Offer'

    def student_display(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.student.id,
            obj.student.get_full_name()
        )
    student_display.short_description = 'Student'

    def teacher_display(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.offer.user.id,
            obj.offer.user.get_full_name()
        )
    teacher_display.short_description = 'Teacher'

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'cancelled': 'red',
            'completed': 'blue',
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification"""
    list_display = [
        'id', 'user_display', 'notification_type_badge',
        'title', 'is_read_badge', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__email', 'user__username', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('exchange_request', 'session', 'booking'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def user_display(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.email
        )
    user_display.short_description = 'User'

    def notification_type_badge(self, obj):
        return format_html(
            '<span style="background-color: #e8f4f8; padding: 3px 10px; border-radius: 3px;">{}</span>',
            obj.get_notification_type_display()
        )
    notification_type_badge.short_description = 'Type'

    def is_read_badge(self, obj):
        if obj.is_read:
            return format_html('<span style="color: green;">✓ Read</span>')
        return format_html('<span style="color: orange;">⦿ Unread</span>')
    is_read_badge.short_description = 'Status'