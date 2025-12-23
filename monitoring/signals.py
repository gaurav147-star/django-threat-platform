from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SecurityEvent, Alert

@receiver(post_save, sender=SecurityEvent)
def create_alert_for_critical_events(sender, instance, created, **kwargs):
    if created:
        if instance.severity in ['HIGH', 'CRITICAL']:
            Alert.objects.create(event=instance)
