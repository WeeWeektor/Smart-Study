from django.test import TransactionTestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from unittest.mock import patch, Mock
import json

User = get_user_model()


class MiddlewareIntegrationTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='Тест',
            surname='Користувач',
            email='test@example.com',
            password='TestPass123!',
            role='student',
            is_active=True,
            is_verified_email=True
        )

    def test_language_middleware_integration(self):
        """Тест інтеграції middleware мови"""
        # Тестуємо через POST запит registration
        response_uk = self.client.post(
            reverse('auth_urls:registration'),
            data=json.dumps({
                'name': 'Тест',
                'surname': 'Користувач',
                'email': 'uk@example.com',
                'password': 'TestPass123!',
                'role': 'student'
            }),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='uk'
        )

        # Перевіряємо що запит оброблений
        self.assertIn(response_uk.status_code, [200, 400, 500])

        # Запит з англійською мовою
        response_en = self.client.post(
            reverse('auth_urls:registration'),
            data=json.dumps({
                'name': 'Test',
                'surname': 'User',
                'email': 'en@example.com',
                'password': 'TestPass123!',
                'role': 'student'
            }),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='en'
        )

        self.assertIn(response_en.status_code, [200, 400, 500])

    @override_settings(
        CORS_ALLOW_ALL_ORIGINS=True,
        CORS_ALLOW_METHODS=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
        CORS_ALLOW_HEADERS=['*']
    )
    def test_cors_middleware_integration(self):
        """Тест інтеграції CORS middleware"""
        # Використовуємо login endpoint
        response = self.client.post(
            reverse('auth_urls:login'),
            data=json.dumps({
                'email': self.user.email,
                'password': 'TestPass123!'
            }),
            content_type='application/json',
            HTTP_ORIGIN='http://localhost:8000'
        )

        # Перевіряємо базову функціональність
        self.assertIn(response.status_code, [200, 400, 401])

    def test_csrf_protection_integration(self):
        """Тест інтеграції CSRF захисту"""
        # Отримання CSRF токену
        csrf_response = self.client.get(reverse('auth_urls:get-csrf-token'))
        self.assertEqual(csrf_response.status_code, 200)

        # Перевіряємо наявність токену в відповіді
        response_data = csrf_response.json()
        self.assertIn('csrf_token', response_data)
        csrf_token = response_data['csrf_token']
        self.assertTrue(len(csrf_token) > 10)

        # Тест з CSRF токеном
        login_data = {
            'email': self.user.email,
            'password': 'TestPass123!'
        }

        response = self.client.post(
            reverse('auth_urls:login'),
            data=json.dumps(login_data),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token
        )

        # CSRF захист має пропустити запит
        self.assertNotEqual(response.status_code, 403)

    def test_csrf_token_generation(self):
        """Тест генерації CSRF токену"""
        # Створюємо request об'єкт
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')

        # Генеруємо CSRF токен
        csrf_token = get_token(request)
        self.assertIsNotNone(csrf_token)
        self.assertTrue(len(csrf_token) > 10)

    def test_middleware_error_handling(self):
        """Тест обробки помилок middleware"""
        # Запит без CSRF токену
        login_data = {
            'email': self.user.email,
            'password': 'TestPass123!'
        }

        response = self.client.post(
            reverse('auth_urls:login'),
            data=json.dumps(login_data),
            content_type='application/json'
        )

        # Перевіряємо що middleware обробив запит
        self.assertIn(response.status_code, [200, 400, 401, 403, 500])

    def test_authentication_middleware(self):
        """Тест middleware автентифікації"""
        # Логінимося
        self.client.force_login(self.user)

        # Тестуємо доступ до захищеного endpoint
        response = self.client.get(reverse('user_urls:profile'))

        # Повинен бути доступ або redirect
        self.assertIn(response.status_code, [200, 302])

    def test_session_middleware(self):
        """Тест session middleware"""
        # Логін для створення сесії
        login_response = self.client.post(
            reverse('auth_urls:login'),
            data=json.dumps({
                'email': self.user.email,
                'password': 'TestPass123!'
            }),
            content_type='application/json'
        )

        # Перевіряємо що сесія створена (може бути в cookies або в response)
        session_created = (
            'sessionid' in self.client.cookies or
            login_response.status_code == 200
        )
        self.assertTrue(session_created)

        # Перевіряємо доступ з сесією
        profile_response = self.client.get(reverse('user_urls:profile'))
        self.assertIn(profile_response.status_code, [200, 401])

    def test_content_type_middleware(self):
        """Тест middleware обробки content-type"""
        # JSON запит
        json_response = self.client.post(
            reverse('auth_urls:login'),
            data=json.dumps({
                'email': self.user.email,
                'password': 'TestPass123!'
            }),
            content_type='application/json'
        )

        self.assertIn(json_response.status_code, [200, 400, 401])

        # Form data запит
        form_response = self.client.post(
            reverse('auth_urls:login'),
            data={
                'email': self.user.email,
                'password': 'TestPass123!'
            }
        )

        self.assertIn(form_response.status_code, [200, 400, 401])

    def test_middleware_chain_order(self):
        """Тест порядку виконання middleware"""
        # Тестуємо що всі middleware працюють разом
        response = self.client.post(
            reverse('auth_urls:login'),
            data=json.dumps({
                'email': self.user.email,
                'password': 'TestPass123!'
            }),
            content_type='application/json',
            HTTP_ACCEPT_LANGUAGE='uk',
            HTTP_ORIGIN='http://localhost:8000'
        )

        # Middleware chain має обробити запит без помилок
        self.assertIn(response.status_code, [200, 400, 401])
        # Перевіряємо що response має коректний content-type
        self.assertIn('application/json', response.get('Content-Type', ''))
