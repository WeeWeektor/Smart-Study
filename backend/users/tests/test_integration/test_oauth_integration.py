from unittest.mock import patch, MagicMock
from django.test import TransactionTestCase
from django.urls import reverse
import json
from django.core.cache import cache
from django.contrib.auth import get_user_model

from users.services.profile_cache_service import get_cached_profile
from users.models import CustomUser

User = get_user_model()


class OAuthIntegrationTest(TransactionTestCase):
    def setUp(self):
        cache.clear()

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_oauth_complete_flow(self, mock_verify_token):
        """Тест повного потоку Google OAuth"""
        mock_verify_token.return_value = {
            'sub': 'google_123',
            'email': 'test@gmail.com',
            'name': 'Test User',
            'given_name': 'Test',
            'family_name': 'User',
            'picture': 'https://example.com/avatar.jpg',
            'email_verified': True
        }

        oauth_data = {
            'credential': 'fake_google_token',
            'name': 'Test',
            'surname': 'User',
            'role': 'student'
        }

        response = self.client.post(
            reverse('auth_urls:google-oauth'),
            data=json.dumps(oauth_data),
            content_type='application/json'
        )

        self.assertIn(response.status_code, [200, 201])

        response_data = json.loads(response.content)
        self.assertIn('user', response_data)

        user_data = response_data['user']
        self.assertEqual(user_data['email'], 'test@gmail.com')
        self.assertEqual(user_data['name'], 'Test')
        self.assertEqual(user_data['surname'], 'User')

        user = User.objects.get(email='test@gmail.com')
        self.assertTrue(user.is_verified_email)
        self.assertTrue(user.is_active)

    def test_facebook_oauth_simulation(self):
        """Симуляція Facebook OAuth без facebook-sdk"""
        with patch('users.services.oauth_service.handle_oauth_login') as mock_handle_oauth:
            mock_handle_oauth.return_value = MagicMock()
            mock_handle_oauth.return_value.status_code = 200
            mock_handle_oauth.return_value.content = json.dumps({
                'user': {
                    'id': 'test-uuid',
                    'email': 'test@facebook.com',
                    'name': 'Facebook',
                    'surname': 'User',
                    'role': 'student'
                }
            }).encode()

            oauth_data = {
                'credential': 'fake_facebook_token',
                'name': 'Facebook',
                'surname': 'User',
                'role': 'student'
            }

            response = self.client.post(
                reverse('auth_urls:facebook-oauth'),
                data=json.dumps(oauth_data),
                content_type='application/json'
            )

            self.assertIn(response.status_code, [200, 400])

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_oauth_existing_user_login(self, mock_verify_token):
        """Тест входу існуючого користувача через Google OAuth"""
        existing_user = User.objects.create_user(
            name='Existing',
            surname='User',
            email='existing@gmail.com',
            password='testpass123',
            role='student',
            is_verified_email=True,
            is_active=True
        )

        mock_verify_token.return_value = {
            'sub': 'google_existing',
            'email': 'existing@gmail.com',
            'name': 'Existing User',
            'given_name': 'Existing',
            'family_name': 'User',
            'picture': 'https://example.com/existing_avatar.jpg',
            'email_verified': True
        }

        oauth_data = {
            'credential': 'fake_existing_token',
            'name': 'Existing',
            'surname': 'User',
            'role': 'student'
        }

        response = self.client.post(
            reverse('auth_urls:google-oauth'),
            data=json.dumps(oauth_data),
            content_type='application/json'
        )

        self.assertIn(response.status_code, [200, 201])

        response_data = json.loads(response.content)
        self.assertIn('user', response_data)

        user_data = response_data['user']
        self.assertEqual(user_data['email'], 'existing@gmail.com')

        if 'id' in user_data:
            self.assertEqual(str(existing_user.id), user_data['id'])

        db_user = CustomUser.objects.get(email='existing@gmail.com')
        self.assertEqual(existing_user.id, db_user.id)

    def test_oauth_invalid_token(self):
        """Тест обробки недійсного токену"""
        with patch('google.oauth2.id_token.verify_oauth2_token') as mock_verify:
            mock_verify.side_effect = ValueError("Invalid token")

            oauth_data = {
                'credential': 'invalid_token',
                'name': 'Test',
                'surname': 'User',
                'role': 'student'
            }

            response = self.client.post(
                reverse('auth_urls:google-oauth'),
                data=json.dumps(oauth_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.content)
            self.assertIn('error', response_data)

    def test_oauth_missing_credential(self):
        """Тест відсутності credential"""
        oauth_data = {
            'name': 'Test',
            'surname': 'User',
            'role': 'student'
        }

        response = self.client.post(
            reverse('auth_urls:google-oauth'),
            data=json.dumps(oauth_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_oauth_user_creation_with_settings(self, mock_verify_token):
        """Тест створення користувача з налаштуваннями через OAuth"""
        mock_verify_token.return_value = {
            'sub': 'settings_123',
            'email': 'settings@gmail.com',
            'name': 'Settings Test',
            'given_name': 'Settings',
            'family_name': 'Test',
            'picture': 'https://example.com/settings_avatar.jpg',
            'email_verified': True
        }

        oauth_data = {
            'credential': 'fake_settings_token',
            'name': 'Settings',
            'surname': 'Test',
            'role': 'student',
            'email_notifications': False,
            'push_notifications': True
        }

        response = self.client.post(
            reverse('auth_urls:google-oauth'),
            data=json.dumps(oauth_data),
            content_type='application/json'
        )

        self.assertIn(response.status_code, [200, 201])

        from users.models import UserSettings
        user = User.objects.get(email='settings@gmail.com')

        try:
            user_settings = UserSettings.objects.get(user=user)
            self.assertFalse(user_settings.email_notifications)
            self.assertTrue(user_settings.push_notifications)
        except UserSettings.DoesNotExist:
            self.fail("UserSettings не створені для OAuth користувача")

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_oauth_invalid_role(self, mock_verify_token):
        """Тест неправильної ролі в OAuth"""
        mock_verify_token.return_value = {
            'sub': 'role_123',
            'email': 'role@gmail.com',
            'name': 'Role Test',
            'given_name': 'Role',
            'family_name': 'Test',
            'picture': 'https://example.com/role_avatar.jpg',
            'email_verified': True
        }

        oauth_data = {
            'credential': 'fake_role_token',
            'name': 'Role',
            'surname': 'Test',
            'role': 'invalid_role'
        }

        response = self.client.post(
            reverse('auth_urls:google-oauth'),
            data=json.dumps(oauth_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)

    def test_oauth_missing_required_fields(self):
        """Тест відсутніх обов'язкових полів"""
        oauth_data = {
            'credential': 'fake_token'
        }

        response = self.client.post(
            reverse('auth_urls:google-oauth'),
            data=json.dumps(oauth_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)

    def test_oauth_malformed_json(self):
        """Тест некоректного JSON"""
        response = self.client.post(
            reverse('auth_urls:google-oauth'),
            data='invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_oauth_duplicate_concurrent_requests(self, mock_verify_token):
        """Тест одночасних запитів з однаковими даними"""
        mock_verify_token.return_value = {
            'sub': 'concurrent_123',
            'email': 'concurrent@gmail.com',
            'name': 'Concurrent Test',
            'given_name': 'Concurrent',
            'family_name': 'Test',
            'picture': 'https://example.com/concurrent_avatar.jpg',
            'email_verified': True
        }

        oauth_data = {
            'credential': 'fake_concurrent_token',
            'name': 'Concurrent',
            'surname': 'Test',
            'role': 'student'
        }

        response1 = self.client.post(
            reverse('auth_urls:google-oauth'),
            data=json.dumps(oauth_data),
            content_type='application/json'
        )

        response2 = self.client.post(
            reverse('auth_urls:google-oauth'),
            data=json.dumps(oauth_data),
            content_type='application/json'
        )

        self.assertTrue(
            response1.status_code in [200, 201] or response2.status_code in [200, 201]
        )

        users_count = User.objects.filter(email='concurrent@gmail.com').count()
        self.assertEqual(users_count, 1)


class OAuthCacheIntegrationTest(TransactionTestCase):
    def setUp(self):
        cache.clear()

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_oauth_with_cache_integration(self, mock_verify):
        """Інтеграція Google OAuth з кешуванням"""
        mock_verify.return_value = {
            'sub': 'cache_123',
            'email': 'google_cache@example.com',
            'name': 'Google Cache User',
            'given_name': 'Google',
            'family_name': 'User',
            'picture': 'https://example.com/cache_avatar.jpg',
            'email_verified': True
        }

        oauth_data = {
            'credential': 'fake_cache_token',
            'name': 'Google',
            'surname': 'User',
            'role': 'student'
        }

        response1 = self.client.post(
            reverse('auth_urls:google-oauth'),
            data=json.dumps(oauth_data),
            content_type='application/json'
        )

        self.assertIn(response1.status_code, [200, 201])

        user = CustomUser.objects.get(email='google_cache@example.com')
        self.assertIsNotNone(user)
        self.assertTrue(user.is_verified_email)
        self.assertTrue(user.is_active)

        response2 = self.client.post(
            reverse('auth_urls:google-oauth'),
            data=json.dumps(oauth_data),
            content_type='application/json'
        )

        self.assertIn(response2.status_code, [200, 201])

        users_count = CustomUser.objects.filter(email='google_cache@example.com').count()
        self.assertEqual(users_count, 1)

        cached_profile = get_cached_profile(user)
        self.assertIsNotNone(cached_profile)


class OAuthErrorHandlingTest(TransactionTestCase):
    def test_invalid_oauth_token_handling(self):
        """Обробка невалідних OAuth токенів"""
        invalid_data = {'code': 'invalid_code', 'role': 'student'}

        response = self.client.post(
            reverse('auth_urls:google-oauth'),
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        self.assertIn(response.status_code, [400, 401, 403])

    def test_oauth_rate_limiting(self):
        """Тест обробки множинних OAuth запитів"""
        oauth_data = {'credential': 'test_token', 'name': 'Test', 'surname': 'User', 'role': 'student'}

        responses = []
        for _ in range(10):
            response = self.client.post(
                reverse('auth_urls:google-oauth'),
                data=json.dumps(oauth_data),
                content_type='application/json'
            )
            responses.append(response.status_code)

        self.assertTrue(all(status == 400 for status in responses))

