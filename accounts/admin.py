from django.contrib import admin
from .models import (
    User,
    SkillCategory,
    Skill,
    UserSkill,
    SkillWanted,
    UserRating
)


# ==============================
# Custom User Admin
# ==============================
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'location',
        'is_active',
        'is_staff',
        'is_email_verified',
        'updated_at',
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_email_verified')
    ordering = ('-updated_at',)


# ==============================
# Skill Category Admin
# ==============================
@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon')
    search_fields = ('name',)
    ordering = ('name',)


# ==============================
# Skill Admin
# ==============================
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    search_fields = ('name',)
    list_filter = ('category',)
    ordering = ('category', 'name')


# ==============================
# User Skill Admin
# ==============================
@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'skill',
        'proficiency_level',
        'years_of_experience',
        'can_teach',
        'created_at',
    )
    search_fields = ('user__email', 'skill__name')
    list_filter = ('proficiency_level', 'can_teach')
    ordering = ('-years_of_experience',)


# ==============================
# Skill Wanted Admin
# ==============================
@admin.register(SkillWanted)
class SkillWantedAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'skill',
        'priority',
        'created_at',
    )
    search_fields = ('user__email', 'skill__name')
    list_filter = ('priority',)
    ordering = ('-priority',)


# ==============================
# User Rating Admin
# ==============================
@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = (
        'rated_user',
        'rated_by',
        'rating',
        'Skill',
        'created_at',
    )
    search_fields = ('rated_user__email', 'rated_by__email')
    list_filter = ('rating',)
    ordering = ('-created_at',)
