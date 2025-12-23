from django.test import TestCase
from .models import SecurityEvent, Alert

class ModelTests(TestCase):
    def test_str_methods(self):
        """Test string representation of models."""
        event = SecurityEvent.objects.create(
            source='GitHub',
            event_type='Push',
            severity='LOW',
            description='Code push'
        )
        self.assertEqual(str(event), "Push (LOW)")
        
        alert = Alert.objects.create(event=event)
        self.assertEqual(str(alert), f"Alert for {event}")

    def test_default_values(self):
        """Test default status of Alert."""
        event = SecurityEvent.objects.create(
            source='S', event_type='T', severity='HIGH', description='D'
        )
        # Manually create without specific status
        alert = Alert.objects.create(event=event)
        self.assertEqual(alert.status, 'OPEN')
