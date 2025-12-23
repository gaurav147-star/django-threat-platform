from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import SecurityEvent, Alert

User = get_user_model()

class ThreatMonitoringTests(APITestCase):
    def setUp(self):
        self.events_url = reverse('event_ingest')
        self.alerts_url = reverse('alert_list')
        
        # Create users
        self.admin = User.objects.create_user(username='admin', password='password', role='ADMIN', is_staff=True)
        self.analyst = User.objects.create_user(username='analyst', password='password', role='ANALYST')
        
        # Create some initial data
        self.high_event = SecurityEvent.objects.create(
            source='Test', event_type='Virus', severity='HIGH', description='Danger'
        )
        self.low_event = SecurityEvent.objects.create(
            source='Test', event_type='Ping', severity='LOW', description='Info'
        )
        # Alert is auto-created for high_event by signals, but we can rely on that or verify it.
        # Let's verify and grab it
        self.alert = Alert.objects.get(event=self.high_event)
        self.detail_url = reverse('alert_status', kwargs={'pk': self.alert.pk})

    def test_ingest_event_unauthenticated(self):
        """Unauthenticated users cannot ingest events."""
        response = self.client.post(self.events_url, {'source': 'Hack', 'event_type': 'X', 'severity': 'HIGH', 'description': 'X'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ingest_valid_event_low_severity(self):
        """Ingesting LOW severity event should NOT create an alert."""
        self.client.force_authenticate(user=self.analyst)
        data = {
            'source': 'Firewall',
            'event_type': 'Connection',
            'severity': 'LOW',
            'description': 'Normal traffic'
        }
        response = self.client.post(self.events_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify NO new alert
        self.assertEqual(Alert.objects.filter(event__description='Normal traffic').count(), 0)

    def test_ingest_valid_event_critical_severity(self):
        """Ingesting CRITICAL severity event SHOULD create an alert."""
        self.client.force_authenticate(user=self.analyst)
        data = {
            'source': 'IDS',
            'event_type': 'Ransomware',
            'severity': 'CRITICAL',
            'description': 'Encrypted files detected'
        }
        response = self.client.post(self.events_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify alert created
        self.assertTrue(Alert.objects.filter(event__description='Encrypted files detected').exists())

    def test_ingest_invalid_severity(self):
        """Ingesting event with invalid choice should fail."""
        self.client.force_authenticate(user=self.analyst)
        data = {
            'source': 'IDS',
            'event_type': 'Bad things',
            'severity': 'EXTREME', # Invalid choice
            'description': '...'
        }
        response = self.client.post(self.events_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('severity', response.data)

    def test_alert_list_permissions(self):
        """Both Admin and Analyst can list alerts."""
        self.client.force_authenticate(user=self.analyst)
        response = self.client.get(self.alerts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.alerts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_alert_list_filtering(self):
        """Test filtering alerts by status."""
        self.client.force_authenticate(user=self.analyst)
        # Filter by OPEN (should find one)
        response = self.client.get(self.alerts_url + '?status=OPEN')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filter by RESOLVED (should find none)
        response = self.client.get(self.alerts_url + '?status=RESOLVED')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_alert_update_permission_denied_for_analyst(self):
        """Analyst cannot update alert status."""
        self.client.force_authenticate(user=self.analyst)
        data = {'status': 'ACKNOWLEDGED'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_alert_update_success_for_admin(self):
        """Admin can update alert status."""
        self.client.force_authenticate(user=self.admin)
        data = {'status': 'ACKNOWLEDGED'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.status, 'ACKNOWLEDGED')

    def test_alert_update_invalid_status(self):
        """Cannot update to an invalid status."""
        self.client.force_authenticate(user=self.admin)
        data = {'status': 'ARCHIVED'} # Invalid
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_alert_update_readonly_fields(self):
        """Attempting to update the event link should be ignored or explicitly failed (depending on checks).
        DRF usually ignores read-only fields in serializer validation.
        But we want to make sure the event relationship didn't change even if we tried.
        """
        self.client.force_authenticate(user=self.admin)
        
        # Create another event to try to swap
        other_event = SecurityEvent.objects.create(
            source='BadActor', event_type='Bad', severity='HIGH', description='Try to swap'
        )
        
        data = {'event': other_event.id, 'status': 'RESOLVED'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.alert.refresh_from_db()
        # Status should change
        self.assertEqual(self.alert.status, 'RESOLVED')
        # Event should NOT change
        self.assertEqual(self.alert.event.id, self.high_event.id)
        self.assertNotEqual(self.alert.event.id, other_event.id)
