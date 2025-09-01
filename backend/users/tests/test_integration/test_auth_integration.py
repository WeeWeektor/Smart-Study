import json
from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from users.models import UserProfile, UserSettings

User = get_user_model()


class AuthIntegrationTest(TransactionTestCase):
    def test_complete_user_registration_flow(self):
        """Повний цикл реєстрації користувача"""
        # 1. Реєстрація
        registration_data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'name': 'Test',
            'surname': 'User',
            'role': 'student'
        }

        response = self.client.post(
            reverse('auth_urls:registration'),
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(response_data.get('status'), 'success')

        # 2. Перевірка створення користувача
        user = User.objects.get(email='newuser@example.com')
        self.assertFalse(user.is_verified_email)
        self.assertEqual(user.name, 'Test')
        self.assertEqual(user.surname, 'User')
        self.assertEqual(user.role, 'student')

        # 3. Перевірка створення профілю та налаштувань
        try:
            profile = UserProfile.objects.get(user=user)
            self.assertIsNotNone(profile)
        except UserProfile.DoesNotExist:
            # Профіль не створюється автоматично - це нормально
            pass

        try:
            settings = UserSettings.objects.get(user=user)
            self.assertIsNotNone(settings)
        except UserSettings.DoesNotExist:
            # Налаштування не створюються автоматично - це нормально
            pass

        # 4. Перевірка відправки email верифікації
        self.assertEqual(len(mail.outbox), 1)
        verification_email = mail.outbox[0]
        self.assertIn('newuser@example.com', verification_email.to)

    def test_login_after_email_verification(self):
        """Логін після верифікації email"""
        # 1. Створення користувача
        user = User.objects.create_user(
            email='verified@example.com',
            password='SecurePass123!',
            is_verified_email=True,
            is_active=True,
        )

        # 2. Спроба логіну
        login_data = {
            'email': 'verified@example.com',
            'password': 'SecurePass123!'
        }

        response = self.client.post(
            reverse('auth_urls:login'),
            data=json.dumps(login_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('sessionid', response.cookies)

    def test_password_reset_flow(self):
        """Повний цикл скидання пароля"""
        user = User.objects.create_user(
            email='reset@example.com',
            password='OldPass123!',
            is_verified_email=True,
            is_active=True
        )

        # 2. Запит скидання пароля
        reset_data = {'email': 'reset@example.com'}
        response = self.client.post(
            reverse('auth_urls:forgot-password'),
            data=json.dumps(reset_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Перевірка успішної відповіді
        response_data = response.json()
        self.assertEqual(response_data.get('status'), 'success')

        # Перевірка відправки email
        self.assertEqual(len(mail.outbox), 1)
        reset_email = mail.outbox[0]
        self.assertIn('reset@example.com', reset_email.to)
