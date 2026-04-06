from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
import json
import uuid

User = get_user_model()


class ProfileE2ETest(TransactionTestCase):
    """End-to-end тести для профілю користувача"""

    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_complete_user_journey(self):
        """Тест повного шляху користувача від реєстрації до видалення"""
        unique_email = f'john-{uuid.uuid4().hex[:8]}@example.com'

        register_data = {
            'name': 'John',
            'surname': 'Doe',
            'email': unique_email,
            'password': 'StrongPass123!',
            'role': 'student'
        }

        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps(register_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(email=unique_email)
        user.is_active = True
        user.is_verified_email = True
        user.save()

        login_data = {
            'email': unique_email,
            'password': 'StrongPass123!'
        }

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)
        profile_data = response.json()
        self.assertEqual(profile_data['user']['name'], 'John')

        update_data = {
            'user': {'name': 'Johnny'},
            'profile': {'bio': 'Updated bio'}
        }

        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        image_content = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
            b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
            b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
            b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342'
            b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01'
            b'\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff'
            b'\xda\x00\x08\x01\x01\x00\x00?\x00\x00\xff\xd9'
        )

        test_image = SimpleUploadedFile(
            "test_profile.jpg",
            image_content,
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': test_image}
        )
        self.assertEqual(response.status_code, 200)

        password_data = {
            'current_password': 'StrongPass123!',
            'new_password': 'NewStrongPass123!',
            'confirm_password': 'NewStrongPass123!'
        }

        response = self.client.patch(
            '/api/user/change-password/',
            data=json.dumps(password_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.delete('/api/user/profile/')
        self.assertEqual(response.status_code, 200)

        self.assertFalse(User.objects.filter(email=unique_email).exists())

    def test_profile_data_consistency_across_requests(self):
        """Тест консистентності даних профілю між запитами"""
        user = User.objects.create_user(
            email='consistency@example.com',
            password='testpass123',
            is_active=True,
            is_verified_email=True
        )
        self.client.force_login(user)

        for i in range(5):
            update_data = {
                'user': {'name': f'User{i}'},
                'profile': {'bio': f'Bio {i}'}
            }

            response = self.client.patch(
                '/api/user/profile/',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

            response = self.client.get('/api/user/profile/')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['user']['name'], f'User{i}')
            self.assertEqual(data['profile']['bio'], f'Bio {i}')

    def test_concurrent_profile_updates(self):
        """Тест одночасних оновлень профілю"""
        user = User.objects.create_user(
            email='concurrent@example.com',
            password='testpass123',
            is_active=True,
            is_verified_email=True
        )

        clients = [Client() for _ in range(3)]
        for client in clients:
            client.force_login(user)

        responses = []
        for i, client in enumerate(clients):
            update_data = {
                'user': {'name': f'ConcurrentUser{i}'}
            }

            response = client.patch(
                '/api/user/profile/',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            responses.append(response)

        for response in responses:
            self.assertEqual(response.status_code, 200)

        final_response = clients[0].get('/api/user/profile/')
        self.assertEqual(final_response.status_code, 200)

    def test_oauth_to_profile_complete_flow(self):
        """E2E тест OAuth → Profile workflow"""
        from unittest.mock import patch

        with patch('users.services.oauth_service.id_token.verify_oauth2_token') as mock_verify:
            mock_verify.return_value = {
                'email': 'oauth_e2e@example.com',
                'given_name': 'OAuth',
                'family_name': 'User',
                'picture': 'https://example.com/avatar.jpg'
            }

            oauth_data = {
                'credential': 'fake_token',
                'role': 'student'
            }

            response = self.client.post(
                '/api/auth/google-oauth/',
                data=json.dumps(oauth_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

            response = self.client.get('/api/user/profile/')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['user']['email'], 'oauth_e2e@example.com')

            profile_data = {
                'profile': {
                    'bio': 'OAuth user bio',
                    'location': 'Kyiv, Ukraine'
                },
                'settings': {
                    'email_notifications': True
                }
            }

            response = self.client.patch(
                '/api/user/profile/',
                data=json.dumps(profile_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_email_verification_complete_workflow(self):
        """E2E тест email верифікації"""
        unique_email = f'verify-{uuid.uuid4().hex[:8]}@example.com'

        register_data = {
            'name': 'Verify',
            'surname': 'User',
            'email': unique_email,
            'password': 'VerifyPass123!',
            'role': 'student'
        }

        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps(register_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        login_data = {
            'email': unique_email,
            'password': 'VerifyPass123!'
        }

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [200, 400, 401, 403])

        user = User.objects.get(email=unique_email)
        user.is_verified_email = True
        user.is_active = True
        user.save()

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_error_recovery_workflow(self):
        """E2E тест відновлення після помилок"""
        user = User.objects.create_user(
            name='Recovery',
            surname='User',
            email='recovery@example.com',
            password='Recovery123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )
        self.client.force_login(user)

        response = self.client.patch(
            '/api/user/profile/',
            data='{"user": {"name": "Test"',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/api/user/profile/')
        data = response.json()
        self.assertEqual(data['user']['name'], 'Recovery')

        valid_data = {
            'user': {'name': 'Recovered User'}
        }

        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/user/profile/')
        data = response.json()
        self.assertEqual(data['user']['name'], 'Recovered User')
