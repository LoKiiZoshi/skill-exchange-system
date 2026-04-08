from django.test import TestCase

# Create your tests here.


from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status


from accounts.models import SkillCategory, Skill, UserSkill, SkillWanted
from. models import(
    MatchPreference, SkillMatch, MatchSuggestion,
    SavedMatch, MatchFilter, MatchFeedback
)

User = get_user_model()

class MatchPreferenceModelTest(TestCase):
    """Tests for MatchPreference model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username= 'testuser',
            email = 'test@example.com',
            password= 'pass123'
        )
    def test_preference_creation(self):
        """Test match preference is created correctly"""
        preference = MatchPreference.objects.create(
            user = self.user,
            max_distance = '10km',
            meeting_preference = 'online_only',
            min_rating = 4.0
        )
        
        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.max_distance,'10km')
        self.assertEqual(preference.meeting_preference,'onlinr_only')
        
        
        
class SkillMatchModelTest(TestCase):
    """Tests for SkillMatch model"""
    
    def setUp(self):
        self.User1 = User.Objects.create_user(
            username = 'user1',
            email = 'user1@example.com',
            password = 'pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email= 'user1@example.com',
            password = 'pass123'
        )
        
        category = SkillCategory.objects.create(name ='Programmin')
        self.skill1 = Skill.objects.create(name = 'Python', category = category)
        self.skill2 = Skill.objects.create(name = 'JavaScript', category = category)
        
        def test_skill_match_creation(self):
            """Test skill match is created correctly"""
            match = SkillMatch.objects.create(
                user1 = self.user1,
                user2 = self.user2,
                user1_skill = self.skill1,
                user2_skill = self.skill2,
                match_type = 'mutual_exchange',
                match_type = 'mutual_exchange',
                match_score = 85.5,
                skill_compatibility = 20.0,
                experience_compatibility = 15.0,
                rating_compatibility = 10.5
            )
            
            self.assertEqual(match.match_score, 85.5)
            self.assertEqual(match.match_type,'mutual_exchange')
            self.assertTrue(match.is_active)
            