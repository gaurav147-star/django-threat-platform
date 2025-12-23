from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('token_obtain_pair')
        self.admin_user = User.objects.create_user(username='admin', password='password123', role='ADMIN')

    def test_register_analyst(self):
        """Ensure we can register a new analyst user."""
        data = {
            'username': 'newuser',
            'password': 'password123',
            'email': 'test@example.com',
            'role': 'ANALYST'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username='newuser').role, 'ANALYST')

    def test_login_success(self):
        """Ensure valid credentials return a JWT token."""
        data = {
            'username': 'admin',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """Ensure invalid credentials fail."""
        data = {
            'username': 'admin',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        """Ensure missing fields are handled."""
        data = {
            'username': 'admin'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
