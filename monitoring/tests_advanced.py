from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import SecurityEvent, Alert

User = get_user_model()

class AdvancedIntegrationTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='password', role='ADMIN', is_staff=True)
        self.analyst = User.objects.create_user(username='analyst', password='password', role='ANALYST')
        
        # Seed Data for Pagination/Filtering
        self.event_high = SecurityEvent.objects.create(source='S1', event_type='T1', severity='HIGH', description='Critical error')
        self.event_low = SecurityEvent.objects.create(source='S2', event_type='T2', severity='LOW', description='Just info')
        self.alert_high = Alert.objects.get(event=self.event_high) # Auto-created

    def test_method_not_allowed(self):
        """Verify handling of disallowed HTTP methods on endpoints."""
        self.client.force_authenticate(user=self.admin)
        
        # DELETE /api/events/ (Not allowed, only POST)
        response = self.client.delete(reverse('event_ingest'))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # DELETE /api/alerts/{id}/ (Not allowed, Read-Only or Update status only)
        # Assuming we didn't implement DestroyModelMixin
        detail_url = reverse('alert_detail', kwargs={'pk': self.alert_high.pk})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_search_functionality(self):
        """Test searching alerts by event fields."""
        self.client.force_authenticate(user=self.analyst)
        url = reverse('alert_list')
        
        # Search for 'Critical' (in description)
        response = self.client.get(url + '?search=Critical')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.alert_high.id)
        
        # Search for 'Banana' (non-existent)
        response = self.client.get(url + '?search=Banana')
        self.assertEqual(len(response.data['results']), 0)

    def test_pagination(self):
        """Test pagination response structure."""
        # Create enough alerts to trigger pagination (PAGE_SIZE=10 in settings)
        for i in range(15):
            e = SecurityEvent.objects.create(source=f'Bulk{i}', event_type='T', severity='HIGH', description='D')
        
        self.client.force_authenticate(user=self.analyst)
        url = reverse('alert_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(len(response.data['results']), 10) # Default page size

        # Go to next page
        next_page = response.data['next']
        response = self.client.get(next_page)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Total 1 + 15 = 16 alerts. Page 1 has 10. Page 2 should have 6.
        self.assertEqual(len(response.data['results']), 6)

    def test_update_status_idempotency(self):
        """Updating status to the same value works."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('alert_status', kwargs={'pk': self.alert_high.pk})
        
        # Sets to ACKNOWLEDGED
        self.client.patch(url, {'status': 'ACKNOWLEDGED'})
        self.alert_high.refresh_from_db()
        self.assertEqual(self.alert_high.status, 'ACKNOWLEDGED')
        
        # Sets to ACKNOWLEDGED again
        response = self.client.patch(url, {'status': 'ACKNOWLEDGED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alert_high.refresh_from_db()
        self.assertEqual(self.alert_high.status, 'ACKNOWLEDGED')
