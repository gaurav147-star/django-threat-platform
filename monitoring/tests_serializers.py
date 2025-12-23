from django.test import TestCase
from .serializers import SecurityEventSerializer, AlertSerializer
from .models import SecurityEvent, Alert

class SerializerTests(TestCase):
    def test_security_event_serializer_validation(self):
        """Test strict validation of SecurityEventSerializer."""
        # Missing required field
        invalid_data = {
            'source': 'Test',
            'severity': 'LOW'
            # Missing event_type, description
        }
        serializer = SecurityEventSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('event_type', serializer.errors)
        self.assertIn('description', serializer.errors)

        # Invalid severity choice
        invalid_severity = {
            'source': 'Test',
            'event_type': 'Test',
            'description': 'Test',
            'severity': 'CAT_ON_KEYBOARD'
        }
        serializer = SecurityEventSerializer(data=invalid_severity)
        self.assertFalse(serializer.is_valid())
        self.assertIn('severity', serializer.errors)

    def test_security_event_max_length(self):
        """Test boundary conditions for char fields."""
        long_string = 'a' * 101 # Max is 100
        data = {
            'source': long_string,
            'event_type': 'Test',
            'severity': 'LOW',
            'description': 'Test'
        }
        serializer = SecurityEventSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('source', serializer.errors)

    def test_alert_serializer_readonly(self):
        """Test that read-only fields cannot be written via serializer."""
        # Create an event to link
        event = SecurityEvent.objects.create(
            source='S', event_type='T', severity='HIGH', description='D'
        )
        
        # Try to pass a 'created_at' in data (should be ignored or handled)
        # and try to set 'event_details' (read only)
        data = {
            'event': event.id,
            'status': 'OPEN',
            'created_at': '2000-01-01T00:00:00Z'
        }
        serializer = AlertSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        # event is read_only in serializer, so it's stripped from validated_data.
        # We must provide it to save() to satisfy DB constraint.
        instance = serializer.save(event=event)
        
        # Verify created_at was NOT set to the past
        self.assertNotEqual(instance.created_at.year, 2000)
