from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'


    verbose_name = 'User Accounts & Skills'
    
    def ready(self):
        # Import signals here if needed
        pass