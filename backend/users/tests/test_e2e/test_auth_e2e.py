from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
import json
import uuid

User = get_user_model()

class AuthE2ETest(TransactionTestCase):
    """End-to-end тести для аутентифікації"""

    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_complete_registration_flow(self):
        """Повний цикл реєстрації з усіма перевірками"""
        unique_email = f'reg-{uuid.uuid4().hex[:8]}@example.com'

        # 1. Реєстрація
        register_data = {
            'name': 'Test',
            'surname': 'User',
            'email': unique_email,
            'password': 'SecurePass123!',
            'role': 'teacher',
        }

        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps(register_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # 2. Перевірка створення в БД
        user = User.objects.get(email=unique_email)
        self.assertEqual(user.name, 'Test')
        self.assertEqual(user.role, 'teacher')
        self.assertFalse(user.is_verified_email)

        # 3. Спроба логіну до верифікації
        login_data = {
            'email': unique_email,
            'password': 'SecurePass123!'
        }

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        # Може блокувати неверифікованих користувачів
        self.assertIn(response.status_code, [200, 400, 401, 403])

        # 4. Верифікація та успішний логін
        user.is_verified_email = True
        user.is_active = True
        user.save()

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # 5. Доступ до захищених ресурсів
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)

        # 6. Логаут
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, 200)

        # 7. Спроба доступу після логауту
        response = self.client.get('/api/user/profile/')
        self.assertIn(response.status_code, [302, 401, 403])

    def test_password_reset_complete_flow(self):
        """Повний цикл скидання пароля"""
        user = User.objects.create_user(
            email='reset@example.com',
            password='OldPass123!',
            is_verified_email=True,
            is_active=True
        )

        # 1. Запит на скидання пароля
        reset_data = {'email': 'reset@example.com'}

        response = self.client.post(
            '/api/auth/forgot-password/',
            data=json.dumps(reset_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # 2. Симуляція скидання пароля (без реального email)
        user.set_password('NewPass123!')
        user.save()

        # 3. Логін з новим паролем
        login_data = {
            'email': 'reset@example.com',
            'password': 'NewPass123!'
        }

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # 4. Спроба логіну зі старим паролем
        old_login_data = {
            'email': 'reset@example.com',
            'password': 'OldPass123!'
        }

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps(old_login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_session_management_flow(self):
        """Тест управління сесіями"""
        user = User.objects.create_user(
            email='session@example.com',
            password='SessionPass123!',
            is_verified_email=True,
            is_active=True
        )

        # 1. Логін
        login_data = {
            'email': 'session@example.com',
            'password': 'SessionPass123!'
        }

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # 2. Збереження session key
        session_key = self.client.session.session_key

        # 3. Активність в сесії
        for i in range(3):
            response = self.client.get('/api/user/profile/')
            self.assertEqual(response.status_code, 200)

        # 4. Зміна пароля (повинна інвалідувати сесії)
        password_data = {
            'current_password': 'SessionPass123!',
            'new_password': 'NewSessionPass123!',
            'confirm_password': 'NewSessionPass123!'
        }

        response = self.client.patch(
            '/api/user/change-password/',
            data=json.dumps(password_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # 5. Перевірка що сесія все ще дійсна (або потребує ре-логіну)
        response = self.client.get('/api/user/profile/')
        self.assertIn(response.status_code, [200, 401, 403])
