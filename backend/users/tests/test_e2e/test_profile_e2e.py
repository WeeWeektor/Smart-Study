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

        # 1. Реєстрація
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

        # 2. Отримуємо створеного користувача з БД
        user = User.objects.get(email=unique_email)
        user.is_active = True
        user.is_verified_email = True
        user.save()

        # 3. Логін
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

        # 4. Отримання профілю
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)
        profile_data = response.json()
        self.assertEqual(profile_data['user']['name'], 'John')

        # 5. Оновлення профілю
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

        # 6. Завантаження аватара
        test_image = SimpleUploadedFile(
            "avatar.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': test_image}
        )
        self.assertEqual(response.status_code, 200)

        # 7. Зміна пароля
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

        # 8. Видалення акаунту
        response = self.client.delete('/api/user/profile/')
        self.assertEqual(response.status_code, 200)

        # 9. Перевірка що користувач видалений
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

        # Множинні оновлення
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

            # Перевірка що дані збереглися
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

        # Створюємо кілька клієнтів
        clients = [Client() for _ in range(3)]
        for client in clients:
            client.force_login(user)

        # Одночасні оновлення
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

        # Всі запити повинні бути успішними
        for response in responses:
            self.assertEqual(response.status_code, 200)

        # Фінальна перевірка стану
        final_response = clients[0].get('/api/user/profile/')
        self.assertEqual(final_response.status_code, 200)
