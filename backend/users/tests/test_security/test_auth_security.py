import time
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


class AuthSecurityTest(TestCase):
    """Тести безпеки аутентифікації"""

    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_timing_attack_protection(self):
        """Тест захисту від timing атак"""
        # Створення реального користувача
        User.objects.create_user(
            email='real@example.com',
            password='RealPass123!',
            is_verified_email=True
        )

        # Тестування timing для існуючого vs неіснуючого користувача
        times_existing = []
        times_nonexisting = []

        for _ in range(10):
            # Існуючий користувач з неправильним паролем
            start = time.time()
            self.client.post('/api/auth/login/', {
                'email': 'real@example.com',
                'password': 'WrongPassword123!'
            })
            times_existing.append(time.time() - start)

            # Неіснуючий користувач
            start = time.time()
            self.client.post('/api/auth/login/', {
                'email': 'nonexistent@example.com',
                'password': 'WrongPassword123!'
            })
            times_nonexisting.append(time.time() - start)

        avg_existing = sum(times_existing) / len(times_existing)
        avg_nonexisting = sum(times_nonexisting) / len(times_nonexisting)

        # Різниця в часі не повинна бути значною
        time_difference = abs(avg_existing - avg_nonexisting)
        self.assertLess(time_difference, 0.1, "Timing attack protection failed")

    def test_session_fixation_protection(self):
        """Тест захисту від session fixation"""
        # Отримання session ID до логіну
        response = self.client.get('/api/user/profile/')
        old_session_id = self.client.session.session_key

        # Створення і логін користувача
        user = User.objects.create_user(
            email='session_fix@example.com',
            password='SessionFix123!',
            is_verified_email=True,
            is_active=True
        )

        login_response = self.client.post('/api/auth/login/', {
            'email': 'session_fix@example.com',
            'password': 'SessionFix123!'
        })

        # Session ID повинен змінитись після логіну
        new_session_id = self.client.session.session_key
        self.assertNotEqual(old_session_id, new_session_id)
        self.assertEqual(login_response.status_code, 200)

    def test_password_policy_enforcement(self):
        """Тест політики паролів"""
        weak_passwords = [
            '123456',  # Занадто простий
            'password',  # Словниковий
            'qwerty123',  # Популярний pattern
            'abc123',  # Занадто короткий
            'PASSWORD123',  # Без малих літер
            'password123',  # Без великих літер
            'Password',  # Без цифр
            'Passwordd123',  # Без спеціальних символів
        ]

        for weak_pass in weak_passwords:
            response = self.client.post('/api/auth/register/', {
                'name': 'Test',
                'surname': 'User',
                'email': f'weak_{hash(weak_pass)}@example.com',
                'password': weak_pass,
                'role': 'student'
            })

            # Слабкі паролі повинні відхилятись
            self.assertEqual(response.status_code, 400)

    def test_account_enumeration_protection(self):
        """Тест захисту від enumeration атак"""
        # Створення користувача
        User.objects.create_user(
            email='enum_test@example.com',
            password='EnumTest123!',
            is_verified_email=True,
            is_active=True
        )

        # Тест reset password для існуючого email
        response_existing = self.client.post('/api/auth/forgot-password/', {
            'email': 'enum_test@example.com'
        })

        # Тест reset password для неіснуючого email
        response_nonexisting = self.client.post('/api/auth/forgot-password/', {
            'email': 'nonexistent@example.com'
        })

        # Відповіді повинні бути однаковими (не розкривати існування акаунту)
        self.assertEqual(response_existing.status_code, response_nonexisting.status_code)

    def test_csrf_protection(self):
        """Тест CSRF захисту"""
        # Створення користувача
        user = User.objects.create_user(
            email='csrf@example.com',
            password='CSRF123!',
            is_verified_email=True
        )

        # Спроба POST без CSRF токену
        client_no_csrf = Client(enforce_csrf_checks=True)

        response = client_no_csrf.post('/api/auth/login/', {
            'email': 'csrf@example.com',
            'password': 'CSRF123!'
        })

        # CSRF захист повинен блокувати
        self.assertEqual(response.status_code, 403)

    def test_jwt_security(self):
        """Тест безпеки JWT токенів"""
        user = User.objects.create_user(
            email='jwt@example.com',
            password='JWT123!',
            is_verified_email=True
        )

        # Логін та отримання токену
        login_response = self.client.post('/api/auth/login/', {
            'email': 'jwt@example.com',
            'password': 'JWT123!'
        })

        if 'token' in login_response.json():
            token = login_response.json()['token']

            # Тест модифікованого токену
            modified_token = token[:-5] + 'XXXXX'

            response = self.client.get(
                '/api/user/profile/',
                HTTP_AUTHORIZATION=f'Bearer {modified_token}'
            )

            # Модифікований токен повинен відхилятись
            self.assertEqual(response.status_code, 401)

    def test_password_reset_token_security(self):
        """Тест безпеки токенів скидання пароля"""
        user = User.objects.create_user(
            email='reset_sec@example.com',
            password='ResetSec123!',
            is_verified_email=True,
            is_active=True
        )

        # Запит на скидання
        self.client.post('/api/auth/forgot-password/', {
            'email': 'reset_sec@example.com'
        })

        # Симуляція використання недійсного токену
        invalid_tokens = [
            'invalid_token',
            '12345',
            'a' * 100,
            '',
            None
        ]

        for invalid_token in invalid_tokens:
            response = self.client.post('/api/auth/reset-password/', {
                'token': invalid_token,
                'password': 'NewPassword123!'
            })

            # Недійсні токени повинні відхилятись
            self.assertIn(response.status_code, [400, 401, 404])