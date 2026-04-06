from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from unittest.mock import patch
import json
import uuid
from users.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class IntegrationE2ETest(TransactionTestCase):
    """End-to-end тести інтеграції з зовнішніми сервісами"""

    def setUp(self):
        self.client = Client()
        cache.clear()

    @patch('users.views.handle_profile_picture')
    def test_supabase_integration_workflow(self, mock_handle_picture):
        """E2E тест інтеграції з Supabase"""
        mock_handle_picture.return_value = None

        user = User.objects.create_user(
            name='Supabase',
            surname='User',
            email='supabase@example.com',
            password='SupabaseTest123!',
            role='student',
            is_verified_email=True,
            is_active=True,
        )

        user_profile = UserProfile.objects.create(user=user)
        self.client.force_login(user)

        test_file = SimpleUploadedFile(
            "test.jpg",
            b"test file content",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': test_file}
        )

        self.assertEqual(response.status_code, 200)

        mock_handle_picture.assert_called_once()

        call_args = mock_handle_picture.call_args
        self.assertIsNotNone(call_args)
        user_profile_arg = call_args[0][0]
        self.assertEqual(user_profile_arg.user.email, 'supabase@example.com')

    def test_cache_invalidation_across_requests(self):
        """E2E тест інвалідації кешу"""
        user = User.objects.create_user(
            name='Cache',
            surname='User',
            email='cache_e2e@example.com',
            password='CacheTest123!',
            role='student',
            is_verified_email=True,
            is_active=True,
        )
        self.client.force_login(user)

        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)
        original_name = response.json()['user']['name']

        update_data = {
            'user': {'name': 'Updated Name'}
        }

        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)
        updated_name = response.json()['user']['name']

        self.assertNotEqual(original_name, updated_name)
        self.assertEqual(updated_name, 'Updated Name')

    def test_cross_service_data_consistency(self):
        """E2E тест консистентності даних між сервісами"""
        unique_email = f'consistency-{uuid.uuid4().hex[:8]}@example.com'

        register_data = {
            'name': 'Consistent',
            'surname': 'User',
            'email': unique_email,
            'password': 'ConsistentPass123!',
            'role': 'student'
        }

        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps(register_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(email=unique_email)
        self.assertEqual(user.name, 'Consistent')
        self.assertEqual(user.role, 'student')

        user.is_verified_email = True
        user.is_active = True
        user.save()

        login_data = {
            'email': unique_email,
            'password': 'ConsistentPass123!'
        }

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/user/profile/')
        api_data = response.json()

        self.assertEqual(api_data['user']['name'], user.name)
        self.assertEqual(api_data['user']['email'], user.email)
        self.assertEqual(api_data['user']['role'], user.role)

    @patch('users.views.handle_profile_picture')
    def test_supabase_integration_workflow_with_view_patch(self, mock_handle_picture):
        """E2E тест інтеграції з Supabase з патчем у views"""
        mock_handle_picture.return_value = None

        user = User.objects.create_user(
            name='Supabase',
            surname='User',
            email='supabase@example.com',
            password='SupabaseTest123!',
            role='student',
            is_verified_email=True,
            is_active=True,
        )

        user_profile = UserProfile.objects.create(user=user)
        self.client.force_login(user)

        test_file = SimpleUploadedFile(
            "test.jpg",
            b"test file content",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': test_file}
        )

        self.assertEqual(response.status_code, 200)

        mock_handle_picture.assert_called_once()

        call_args = mock_handle_picture.call_args
        self.assertIsNotNone(call_args)
        user_profile_arg = call_args[0][0]
        self.assertEqual(user_profile_arg.user.email, 'supabase@example.com')
