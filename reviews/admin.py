from django.contrib import admin

# Register your models here.
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id','reviewer','reviewed_user','listing_title','rating','created_at']
    list_filter = ['rating','created_at']
    search_fields = ['reviewer__username','reviewed_user__username','listing_title','title','body']
    ordering = ['-created_at']
    readonly_fields = ['created_at','updated_at']
    
    fieldsets = (
        ('Review Target',{
            'fields':('listing_id','listing_title','reviewed_user')
        })
        
        ('Review Content',{
            'fields':('reviewer','rating','title','body')
        })
        
        ('Timestamps',{
            'fields':('created_at','rating','updated_at'),
            'classes':('collapse',),
        }),
        
    )