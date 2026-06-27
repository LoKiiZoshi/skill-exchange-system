"""
profiles/urls.py
Default REST routes for the profile app.

Include in your root urls.py:
    path('api/v1/', include('profiles.urls')),
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserProfileViewSet,
    EducationViewSet,
    ExperienceViewSet,
    CertificationViewSet,
    ProjectViewSet,
    AchievementViewSet,
    ProfileViewViewSet,
    FollowViewSet,
)

router = DefaultRouter()

# ── Core profile ──────────────────────────────────────────────
# GET    /profiles/              list all public profiles
# POST   /profiles/              create own profile
# GET    /profiles/me/           current user's profile
# GET    /profiles/{id}/         retrieve (records a view)
# PUT    /profiles/{id}/         full update
# PATCH  /profiles/{id}/         partial update
# DELETE /profiles/{id}/         delete
# POST   /profiles/{id}/verify/  verify (admin only)
router.register(r'profiles', UserProfileViewSet, basename='profile')

# ── Education ─────────────────────────────────────────────────
# GET    /education/             list own entries
# POST   /education/             create
# GET    /education/{id}/        detail
# PUT    /education/{id}/        update
# PATCH  /education/{id}/        partial update
# DELETE /education/{id}/        delete
router.register(r'education', EducationViewSet, basename='education')

# ── Experience ────────────────────────────────────────────────
# GET    /experience/            list own entries
# POST   /experience/            create
# GET    /experience/{id}/       detail
# PUT    /experience/{id}/       update
# PATCH  /experience/{id}/       partial update
# DELETE /experience/{id}/       delete
router.register(r'experience', ExperienceViewSet, basename='experience')

# ── Certifications ────────────────────────────────────────────
# GET    /certifications/        list own entries
# POST   /certifications/        create
# GET    /certifications/{id}/   detail
# PUT    /certifications/{id}/   update
# PATCH  /certifications/{id}/   partial update
# DELETE /certifications/{id}/   delete
router.register(r'certifications', CertificationViewSet, basename='certification')

# ── Projects ──────────────────────────────────────────────────
# GET    /projects/              list all (public)
# POST   /projects/              create
# GET    /projects/featured/     featured projects
# GET    /projects/mine/         own projects
# GET    /projects/{id}/         detail (increments views)
# PUT    /projects/{id}/         update
# PATCH  /projects/{id}/         partial update
# DELETE /projects/{id}/         delete
# POST   /projects/{id}/like/    like a project
router.register(r'projects', ProjectViewSet, basename='project')

# ── Achievements ──────────────────────────────────────────────
# GET    /achievements/          list own achievements
# POST   /achievements/          create
# GET    /achievements/unlocked/ unlocked achievements
# GET    /achievements/{id}/     detail
# PUT    /achievements/{id}/     update
# PATCH  /achievements/{id}/     partial update
# DELETE /achievements/{id}/     delete
router.register(r'achievements', AchievementViewSet, basename='achievement')

# ── Profile Views (read-only) ─────────────────────────────────
# GET    /profile-views/         views received by current user
# GET    /profile-views/{id}/    detail
router.register(r'profile-views', ProfileViewViewSet, basename='profile-view')

# ── Follows ───────────────────────────────────────────────────
# GET    /follows/               who current user follows
# POST   /follows/               follow someone { "following": <id> }
# DELETE /follows/{id}/          unfollow
# GET    /follows/followers/     who follows current user
# GET    /follows/following/     alias for list
router.register(r'follows', FollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
]