from django.apps import AppConfig


class MatchingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'matching'
    verbose_name = 'Intelligent Matching System'

    def ready(self):
        # Import signals here if needed
        pass