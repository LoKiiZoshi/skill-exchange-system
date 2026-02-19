from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save,sender=User)
def user_created(sender,instance,created,**kwargs):
    """Signal handler for when a new user is created. 
    can be used to send welcome emails, create defaul data, etc. """
    
    
    if created:
        # Add any post-creation logic here
        # For example: send welcome email, create defult profile settingss, etc.
        
        print(f"New user created:{instance.email}")
        
        
        # You can add email verfication logic here
        # Send_verification_email(instance
        # 
        # 
        # )