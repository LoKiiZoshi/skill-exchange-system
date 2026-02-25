from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import ExchangeRequest, ExchangeSession, Booking, Notification


@receiver(post_save, sender=ExchangeRequest)
def exchange_request_created(sender, instance, created, **kwargs):
    """
    Create notification when exchange request is created
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            notification_type='exchange_request',
            title='New Exchange Request',
            message=f'{instance.requester.get_full_name()} wants to exchange {instance.skill_requested.name} for {instance.skill_offered.name}',
            exchange_request=instance
        )


@receiver(post_save, sender=ExchangeSession)
def session_created(sender, instance, created, **kwargs):
    """
    Send notifications when session is created
    """
    if created:
        # Notify both participants
        for participant in [instance.participant_1, instance.participant_2]:
            Notification.objects.create(
                user=participant,
                notification_type='session_reminder',
                title='New Session Scheduled',
                message=f'A new session "{instance.title}" has been scheduled for {instance.scheduled_start.strftime("%Y-%m-%d %H:%M")}',
                session=instance
            )


@receiver(post_save, sender=Booking)
def booking_created(sender, instance, created, **kwargs):
    """
    Create notification when booking is created
    """
    if created:
        Notification.objects.create(
            user=instance.offer.user,
            notification_type='booking_request',
            title='New Booking Request',
            message=f'{instance.student.get_full_name()} wants to book "{instance.offer.title}"',
            booking=instance
        )


@receiver(pre_save, sender=ExchangeSession)
def session_status_changed(sender, instance, **kwargs):
    """
    Handle session status changes
    """
    if instance.pk:
        try:
            old_instance = ExchangeSession.objects.get(pk=instance.pk)
            
            # If session completed, update offer stats if applicable
            if old_instance.status != 'completed' and instance.status == 'completed':
                # Check if this session is from an offer booking
                if hasattr(instance, 'booking') and instance.booking:
                    offer = instance.booking.offer
                    offer.total_sessions += 1
                    
                    # Update total students (unique students)
                    unique_students = Booking.objects.filter(
                        offer=offer,
                        status='completed'
                    ).values('student').distinct().count()
                    
                    offer.total_students = unique_students
                    offer.save()
        except ExchangeSession.DoesNotExist:
            pass