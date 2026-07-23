from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import SkiSession, SessionMessage

class SessionMessageInline(admin.TabularInline):
    model = SessionMessage
    extra = 0
    readonly_fields = ['sender','body','is_read','created_at']
    can_delete = False
    
   
   
@admin.register(SkiSession)
class SkiSessionAdmin(admin.ModelAdmin):
    list_display    = [
        'id', 'title', 'session_type', 'host', 'participant',
        'skill_level', 'status', 'start_time', 'end_time',
        'duration_hours', 'total_price',
    ]
    list_filter     = ['status', 'session_type', 'skill_level', 'start_time']
    search_fields   = ['title', 'description', 'location',
                       'host__username', 'participant__username', 'listing_title']
    ordering        = ['-start_time']
    readonly_fields = ['duration_hours', 'total_price', 'created_at', 'updated_at']
    inlines         = [SessionMessageInline]
 
    fieldsets = (
        ('Participants', {
            'fields': ('host', 'participant'),
        }),
        ('Session Info', {
            'fields': ('session_type', 'title', 'description', 'skill_level', 'status',
                       'cancellation_reason'),
        }),
        ('Linked Listing', {
            'fields': ('listing_id', 'listing_title'),
            'classes': ('collapse',),
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude'),
            'classes': ('collapse',),
        }),
        ('Schedule & Pricing', {
            'fields': ('start_time', 'end_time', 'duration_hours',
                       'price_per_hour', 'total_price'),
        }),
        ('Notes', {
            'fields': ('host_notes', 'participant_notes'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
 