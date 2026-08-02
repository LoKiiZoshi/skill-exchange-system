from django.contrib import admin
from .models import (
UserProfile,
Education,
Experience,
Certification,
Project,
Achievement,
ProfileView,
Follow,
Block,
ProfileReport,
SocialLink,
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
'user',
'headline',
'profile_visibility',
'is_verified',
'profile_views',
'last_active',
)
list_filter = ('profile_visibility', 'is_verified')
search_fields = ('user__email', 'headline', 'about')
readonly_fields = ('profile_views', 'last_active', 'created_at', 'updated_at')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
   list_display = (
'user',
'institution',
'degree',
'start_date',
'end_date',
'is_current',
)
list_filter = ('is_current',)
search_fields = ('user__email', 'institution', 'degree')

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
 list_display = (
'user',
'title',
'company',
'employment_type',
'start_date',
'end_date',
'is_current',
)
list_filter = ('employment_type', 'is_current')
search_fields = ('user__email', 'title', 'company')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
  list_display = (
'user',
'name',
'issuing_organization',
'issue_date',
'expiration_date',
'does_not_expire',
)
list_filter = ('does_not_expire',)
search_fields = ('user__email', 'name', 'issuing_organization')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
  list_display = (
'user',
'title',
'status',
'is_featured',
'views',
'likes',
'created_at',
)
list_filter = ('status', 'is_featured')
search_fields = ('user__email', 'title')
filter_horizontal = ('technologies',)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
 list_display = (
'user',
'title',
'achievement_type',
'current_value',
'target_value',
'is_unlocked',
)
list_filter = ('achievement_type', 'is_unlocked')
search_fields = ('user__email', 'title')

@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
 list_display = ('profile', 'viewer', 'ip_address', 'viewed_at')
search_fields = ('profile__email', 'viewer__email')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
 list_display = ('follower', 'following', 'created_at')
search_fields = ('follower__email', 'following__email')

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
 list_display = ('blocker', 'blocked', 'created_at')
search_fields = ('blocker__email', 'blocked__email')

@admin.register(ProfileReport)
class ProfileReportAdmin(admin.ModelAdmin):
 list_display = ('reporter', 'reported', 'reason', 'status', 'created_at')
list_filter = ('reason', 'status')
search_fields = ('reporter__email', 'reported__email')

@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
 list_display = ('user', 'platform', 'url', 'created_at')
list_filter = ('platform',)
search_fields = ('user__email', 'platform')
