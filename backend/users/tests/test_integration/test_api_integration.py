from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class APIIntegrationTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='api@example.com',
            password='TestPass123!',
            is_verified_email=True,
            is_active=True
        )

    def test_api_error_handling(self):
        """Обробка помилок API"""
        invalid_data = {
            'email': 'invalid-email',
            'password': '123',
        }

        response = self.client.post(
            reverse('auth_urls:registration'),
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('message', response_data)


class AsyncAPIIntegrationTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='async_api@example.com',
            password='TestPass123!',
            is_verified_email=True,
            is_active=True
        )

    def test_async_profile_operations_integration(self):
        """Інтеграція async операцій профілю"""
        self.client.force_login(self.user)

        response = self.client.get(reverse('user_urls:profile'))
        self.assertEqual(response.status_code, 200)
        profile_data = response.json()

        update_data = {
            'user': {'name': 'Async Test'},
            'profile': {'bio': 'Async bio'},
            'settings': {'email_notifications': False}
        }

        response = self.client.patch(
            reverse('user_urls:profile'),
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        updated_data = response.json()
        self.assertEqual(updated_data['profile_data']['user']['name'], 'Async Test')
        self.assertEqual(updated_data['profile_data']['profile']['bio'], 'Async bio')
        self.assertEqual(updated_data['profile_data']['settings']['email_notifications'], False)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Async Test')

    def test_concurrent_profile_updates(self):
        """Тест конкурентних оновлень профілю"""
        self.client.force_login(self.user)

        import threading

        results = []

        def update_profile(name_suffix):
            update_data = {
                'user': {'name': f'Concurrent_{name_suffix}'},
                'profile': {'bio': f'Bio_{name_suffix}'}
            }

            response = self.client.patch(
                reverse('user_urls:profile'),
                data=json.dumps(update_data),
                content_type='application/json'
            )
            results.append((name_suffix, response.status_code))

        threads = []
        for i in range(3):
            thread = threading.Thread(target=update_profile, args=(i,))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(results), 3)
        for name_suffix, status_code in results:
            self.assertEqual(status_code, 200)
