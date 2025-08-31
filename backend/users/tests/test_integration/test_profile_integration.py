from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
import json

User = get_user_model()


class ProfileIntegrationTest(TransactionTestCase):
    """Інтеграційні тести для профілю користувача"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)

    def test_complete_profile_workflow(self):
        """Тест повного workflow роботи з профілем"""
        # 1. Отримання профілю
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)

        # 2. Оновлення профілю
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

        # 3. Завантаження аватара
        test_image = SimpleUploadedFile(
            "test.jpg",
            b"fake image data",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': test_image}
        )
        self.assertEqual(response.status_code, 200)

        # 4. Перевірка оновленого профілю
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['user']['name'], 'John')

    def test_profile_with_multipart_data(self):
        """Тест оновлення профілю через multipart/form-data"""
        test_image = SimpleUploadedFile(
            "avatar.jpg",
            b"fake image data",
            content_type="image/jpeg"
        )

        response = self.client.patch(
            '/api/user/profile/',
            {
                'name': 'Updated Name',
                'bio': 'Updated bio',
                'profile_picture': test_image
            }
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


class ProfileCacheIntegrationTest(TestCase):
    """Інтеграційні тести для кешування профілю"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='cache@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)

    def test_cache_invalidation_on_update(self):
        """Тест інвалідації кешу при оновленні"""
        response1 = self.client.get('/api/user/profile/')
        self.assertEqual(response1.status_code, 200)

        profile_data = {'user': {'name': 'New Name'}}
        response2 = self.client.patch(
            '/api/user/profile/',
            data=json.dumps(profile_data),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)

        response3 = self.client.get('/api/user/profile/')
        self.assertEqual(response3.status_code, 200)
        data = response3.json()
        self.assertEqual(data['user']['name'], 'New Name')


class ProfileSecurityIntegrationTest(TestCase):
    """Інтеграційні тести для безпеки профілю"""

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )

    def test_unauthorized_access(self):
        """Тест доступу без авторизації"""
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 401)

        response = self.client.patch('/api/user/profile/')
        self.assertEqual(response.status_code, 401)

        response = self.client.delete('/api/user/profile/')
        self.assertEqual(response.status_code, 401)

    def test_cross_user_access_prevention(self):
        """Тест запобігання доступу до чужого профілю"""
        self.client.force_login(self.user1)

        # Користувач 1 створює профіль
        profile_data = {'user': {'name': 'User1'}}
        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps(profile_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Переключаємося на користувача 2
        self.client.force_login(self.user2)

        # Користувач 2 отримує свій профіль (не профіль користувача 1)
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Перевіряємо що це не дані користувача 1
        self.assertNotEqual(data.get('user', {}).get('name'), 'User1')
