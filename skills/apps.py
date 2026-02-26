from django.apps import AppConfig


class SkillsConfig(AppConfig):
    name = 'skills'


default_auto_field = 'django.db.model.BigAutoField'
name = 'skills'
verbose_name = 'Skill Exchanges & Sessions'
 
def ready(self):
    # Import signals here if needed
    import skills.signals
    