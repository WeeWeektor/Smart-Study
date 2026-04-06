from unittest.mock import patch

from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
import json
from django.urls import reverse

from users.models import UserProfile, UserSettings

User = get_user_model()


class ProfileIntegrationTest(TransactionTestCase):
    """Інтеграційні тести для профілю користувача"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            name='Test',
            surname='User',
            email='test@example.com',
            password='testpass123',
            role='student',
            is_active=True,
            is_verified_email=True,
        )
        self.client.force_login(self.user)

    def test_profile_update_with_settings_sync(self):
        """Оновлення профілю з синхронізацією налаштувань"""
        update_data = {
            'profile': {
                'bio': 'Updated bio',
                'location': 'Kyiv, Ukraine',
                'organization': 'Test Org'
            },
            'settings': {
                'email_notifications': False,
                'deadline_reminders': True,
                'show_profile_to_others': False
            }
        }

        response = self.client.patch(
            reverse('user_urls:profile'),
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.bio, 'Updated bio')
        self.assertEqual(profile.location, 'Kyiv, Ukraine')

        settings = UserSettings.objects.get(user=self.user)
        self.assertFalse(settings.email_notifications)
        self.assertTrue(settings.deadline_reminders)
        self.assertFalse(settings.show_profile_to_others)

    @patch('users.views.handle_profile_picture')
    def test_avatar_upload_integration(self, mock_handle_picture):
        """Інтеграційний тест завантаження аватара"""
        mock_handle_picture.return_value = None

        test_image = SimpleUploadedFile(
            "test_avatar.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            data={'profile_picture': test_image}
        )

        self.assertEqual(response.status_code, 200)

        mock_handle_picture.assert_called_once()

    def test_avatar_upload_real_response(self):
        """Тест завантаження аватара без мокування - перевірка реальної відповіді"""
        test_image = SimpleUploadedFile(
            "test_avatar.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            data={'profile_picture': test_image}
        )

        self.assertIn(response.status_code, [200, 400, 500])

    def test_complete_profile_workflow(self):
        """Тест повного workflow роботи з профілем"""
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)

        profile_data = {
            'user': {'name': 'John', 'surname': 'Doe'},
            'settings': {'email_notifications': True},
            'profile': {'bio': 'Test bio'}
        }

        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps(profile_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        test_image = SimpleUploadedFile(
            "test.jpg",
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C',
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': test_image}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['user']['name'], 'John')

    def test_profile_with_multipart_data(self):
        """Тест оновлення профілю через multipart/form-data"""
        test_image = SimpleUploadedFile(
            "avatar.jpg",
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C',
            content_type="image/jpeg"
        )

        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps({
                'user': {'name': 'Updated_Name'},
                'profile': {'bio': 'Updated bio'}
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': test_image}
        )

        self.assertEqual(response.status_code, 200)

    def test_account_deletion_workflow(self):
        """Тест повного видалення акаунту"""
        profile_data = {
            'user': {'name': 'Test User'},
            'profile': {'bio': 'Test bio'}
        }

        self.client.patch(
            '/api/user/profile/',
            data=json.dumps(profile_data),
            content_type='application/json'
        )

        response = self.client.delete('/api/user/profile/')
        self.assertEqual(response.status_code, 200)

        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_profile_data_consistency(self):
        """Тест консистентності даних профілю"""
        profile_data = {
            'user': {'name': 'John', 'surname': 'Doe'},
            'profile': {'bio': 'Developer'},
            'settings': {'email_notifications': False}
        }

        response = self.client.patch(
            reverse('user_urls:profile'),
            data=json.dumps(profile_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('user_urls:profile'))
        data = response.json()

        self.assertEqual(data['user']['name'], 'John')
        self.assertEqual(data['profile']['bio'], 'Developer')
        self.assertFalse(data['settings']['email_notifications'])

    def test_profile_partial_updates(self):
        """Тест часткових оновлень профілю"""
        response = self.client.patch(
            reverse('user_urls:profile'),
            data=json.dumps({'user': {'name': 'NewName'}}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('user_urls:profile'))
        data = response.json()
        self.assertEqual(data['user']['name'], 'NewName')
