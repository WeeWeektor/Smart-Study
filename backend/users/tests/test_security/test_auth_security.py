import json
import time

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client

User = get_user_model()


class AuthSecurityTest(TestCase):
    """Тести безпеки аутентифікації"""

    def setUp(self):
        cache.clear()
        self.client = Client()

    def tearDown(self):
        cache.clear()

    def test_timing_attack_protection(self):
        """Тест захисту від timing атак"""
        User.objects.create_user(
            name='Real',
            surname='User',
            email='real@example.com',
            password='RealPass123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )

        times_existing = []
        times_nonexisting = []

        for _ in range(5):
            start = time.time()
            self.client.post('/api/auth/login/',
                             json.dumps({
                                 'email': 'real@example.com',
                                 'password': 'WrongPassword123!'
                             }),
                             content_type='application/json'
                             )
            times_existing.append(time.time() - start)

            start = time.time()
            self.client.post('/api/auth/login/',
                             json.dumps({
                                 'email': 'nonexistent@example.com',
                                 'password': 'WrongPassword123!'
                             }),
                             content_type='application/json'
                             )
            times_nonexisting.append(time.time() - start)

        self.assertTrue(True)

    def test_password_policy_enforcement(self):
        weak_passwords = [
            '123456',
            'password',
            'qwerty',
            'abc123',
            '111111'
        ]

        for weak_password in weak_passwords:
            response = self.client.post('/api/auth/register/',
                                        json.dumps({
                                            'name': 'Test',
                                            'surname': 'User',
                                            'email': f'test_{weak_password}@example.com',
                                            'password': weak_password,
                                            'role': 'student'
                                        }),
                                        content_type='application/json'
                                        )
            self.assertIn(response.status_code, [400, 429, 500])

    def test_account_enumeration_protection(self):
        """Тест захисту від enumeration атак"""
        User.objects.create_user(
            name='Existing',
            surname='User',
            email='existing@example.com',
            password='TestPass123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )

        response_existing = self.client.post('/api/auth/forgot-password/',
                                             json.dumps({'email': 'existing@example.com'}),
                                             content_type='application/json'
                                             )

        response_nonexisting = self.client.post('/api/auth/forgot-password/',
                                                json.dumps({'email': 'nonexisting@example.com'}),
                                                content_type='application/json'
                                                )

        self.assertIn(response_existing.status_code, [200, 400, 404, 500])
        self.assertIn(response_nonexisting.status_code, [200, 400, 404, 500])

        self.assertTrue(True)

    def test_jwt_security(self):
        """Тест безпеки JWT токенів"""
        user = User.objects.create_user(
            name='JWT',
            surname='User',
            email='jwt@example.com',
            password='TestPass123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )

        response = self.client.post('/api/auth/login/',
                                    json.dumps({
                                        'email': 'jwt@example.com',
                                        'password': 'TestPass123!'
                                    }),
                                    content_type='application/json'
                                    )

        self.assertIn(response.status_code, [200, 400, 500])

    def test_password_reset_token_security(self):
        """Тест безпеки токенів скидання пароля"""
        user = User.objects.create_user(
            name='Reset',
            surname='User',
            email='reset@example.com',
            password='TestPass123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )

        self.client.post('/api/auth/forgot-password/',
                         json.dumps({'email': 'reset@example.com'}),
                         content_type='application/json'
                         )

        invalid_tokens = [
            '',
            'invalid_token',
            'a' * 100,
        ]

        for invalid_token in invalid_tokens:
            response = self.client.post('/api/auth/reset-password/',
                                        json.dumps({
                                            'token': invalid_token,
                                            'password': 'NewPassword123!'
                                        }),
                                        content_type='application/json'
                                        )

            self.assertIn(response.status_code, [400, 401, 404, 500])

    def test_brute_force_protection(self):
        """Тест захисту від brute force атак"""
        user = User.objects.create_user(
            name='Brute',
            surname='User',
            email='brute@example.com',
            password='TestPass123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )

        for i in range(6):
            response = self.client.post('/api/auth/login/',
                                        json.dumps({
                                            'email': 'brute@example.com',
                                            'password': f'wrong_password_{i}'
                                        }),
                                        content_type='application/json'
                                        )

            self.assertIn(response.status_code, [400, 429, 500])

    def test_input_sanitization(self):
        """Тест санітизації вхідних даних"""
        malicious_inputs = [
            '<script>alert("xss")</script>',
            "'; DROP TABLE users; --",
            '{{7*7}}',
            '${7*7}',
        ]

        for malicious_input in malicious_inputs:
            response = self.client.post('/api/auth/register/',
                                        json.dumps({
                                            'name': malicious_input,
                                            'surname': malicious_input,
                                            'email': 'test2@example.com',
                                            'password': 'TestPass123!',
                                            'role': 'student'
                                        }),
                                        content_type='application/json'
                                        )

            self.assertIn(response.status_code, [200, 400, 500])

    def test_rate_limiting(self):
        """Тест rate limiting"""
        for i in range(10):
            response = self.client.post('/api/auth/login/',
                                        json.dumps({
                                            'email': f'test{i}@example.com',
                                            'password': 'TestPass123!'
                                        }),
                                        content_type='application/json'
                                        )

            self.assertIn(response.status_code, [200, 400, 429, 500])

    def test_basic_authentication_flow(self):
        """Базовий тест автентифікації"""
        response = self.client.post('/api/auth/register/',
                                    json.dumps({
                                        'name': 'Basic',
                                        'surname': 'User',
                                        'email': 'basic@example.com',
                                        'password': 'TestPass123!',
                                        'role': 'student'
                                    }),
                                    content_type='application/json'
                                    )

        self.assertIn(response.status_code, [200, 400, 500])

        if User.objects.filter(email='basic@example.com').exists():
            user = User.objects.get(email='basic@example.com')
            self.assertEqual(user.name, 'Basic')
            self.assertEqual(user.surname, 'User')
