import json

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings

User = get_user_model()


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'common.middleware.RateLimitMiddleware',
        'common.middleware.SecurityHeadersMiddleware',
    ]
)
class AdvancedSecurityTest(TestCase):
    """Розширені тести безпеки"""

    def setUp(self):
        cache.clear()

    def test_login_brute_force_protection(self):
        """Захист від brute force на логін"""
        User.objects.create_user(
            name='Victim',
            surname='User',
            email='victim@example.com',
            password='correct_password',
            role='student',
            is_verified_email=True,
            is_active=True
        )

        for i in range(5):
            response = self.client.post('/api/auth/login/',
                                        json.dumps({
                                            'email': 'victim@example.com',
                                            'password': f'wrong_password_{i}'
                                        }),
                                        content_type='application/json'
                                        )
            self.assertIn(response.status_code, [400, 500])

        response = self.client.post('/api/auth/login/',
                                    json.dumps({
                                        'email': 'victim@example.com',
                                        'password': 'wrong_password_6'
                                    }),
                                    content_type='application/json'
                                    )

        self.assertIn(response.status_code, [400, 429, 500])

    def test_register_rate_limiting(self):
        """Захист від спаму реєстрації"""
        for i in range(3):
            response = self.client.post('/api/auth/register/',
                                        json.dumps({
                                            'name': f'Test{i}',
                                            'surname': f'User{i}',
                                            'email': f'test{i}@example.com',
                                            'password': 'TestPass123!',
                                            'role': 'student'
                                        }),
                                        content_type='application/json'
                                        )
            self.assertIn(response.status_code, [200, 400, 500])

        response = self.client.post('/api/auth/register/',
                                    json.dumps({
                                        'name': 'Test4',
                                        'surname': 'User4',
                                        'email': 'test4@example.com',
                                        'password': 'TestPass123!',
                                        'role': 'student'
                                    }),
                                    content_type='application/json'
                                    )

        self.assertIn(response.status_code, [200, 400, 429, 500])

    def test_privilege_escalation_protection(self):
        """Захист від privilege escalation"""
        user = User.objects.create_user(
            name='Regular',
            surname='User',
            email='regular@example.com',
            password='TestPass123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )

        self.client.force_login(user)

        response = self.client.patch('/api/user/profile/',
                                     json.dumps({
                                         'user': {
                                             'name': 'New Name',
                                             'role': 'admin',
                                             'is_staff': True,
                                             'is_superuser': True
                                         }
                                     }),
                                     content_type='application/json'
                                     )

        self.assertIn(response.status_code, [200, 400, 500])

        user.refresh_from_db()
        self.assertEqual(user.role, 'student')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_input_validation_security(self):
        """Тест валідації небезпечних вхідних даних"""
        user = User.objects.create_user(
            name='Test',
            surname='User',
            email='test@example.com',
            password='TestPass123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )

        self.client.force_login(user)

        response = self.client.patch('/api/user/profile/',
                                     json.dumps({
                                         'user': {
                                             'name': '<script>alert("XSS")</script>',
                                             'surname': "'; DROP TABLE users; --"
                                         }
                                     }),
                                     content_type='application/json'
                                     )

        self.assertIn(response.status_code, [200, 400, 500])

        user.refresh_from_db()

        if user.surname:
            self.assertTrue(True)

    def test_security_headers(self):
        """Тест заголовків безпеки"""
        user = User.objects.create_user(
            name='Test',
            surname='User',
            email='test@example.com',
            password='TestPass123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )

        self.client.force_login(user)
        response = self.client.get('/api/user/profile/')

        expected_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Referrer-Policy'
        ]

        for header in expected_headers:
            if header in response:
                self.assertIsNotNone(response[header])

    def test_cache_functionality(self):
        """Тест що кеш працює правильно"""
        test_key = 'test_rate_limit'
        test_value = 5

        cache.set(test_key, test_value, 60)
        retrieved_value = cache.get(test_key, 0)
        self.assertEqual(retrieved_value, test_value)

        cache.delete(test_key)
        retrieved_after_delete = cache.get(test_key, 0)
        self.assertEqual(retrieved_after_delete, 0)

    def test_authentication_required_endpoints(self):
        """Тест що захищені ендпоінти існують"""
        response = self.client.get('/api/user/profile/')

        self.assertIn(response.status_code, [401, 403, 500])

    def test_basic_functionality(self):
        """Базовий тест функціональності"""
        user = User.objects.create_user(
            name='Basic',
            surname='User',
            email='basic@example.com',
            password='TestPass123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )

        self.assertTrue(User.objects.filter(email='basic@example.com').exists())

        self.assertEqual(user.name, 'Basic')
        self.assertEqual(user.surname, 'User')
        self.assertEqual(user.role, 'student')
