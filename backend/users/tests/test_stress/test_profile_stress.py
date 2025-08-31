import threading
import time
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.test import Client
import json

User = get_user_model()


class ProfileStressTest(TransactionTestCase):
    """Stress тести для профілю"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='stress@example.com',
            password='testpass123',
            is_active=True,
            is_verified_email=True
        )

    def test_high_frequency_profile_requests(self):
        """Тест високочастотних запитів до профілю"""
        client = Client()
        client.force_login(self.user)

        success_count = 0
        total_requests = 100

        start_time = time.time()

        for _ in range(total_requests):
            response = client.get('/api/user/profile/')
            if response.status_code == 200:
                success_count += 1

        end_time = time.time()

        self.assertGreaterEqual(success_count / total_requests, 0.95)

        avg_time = (end_time - start_time) / total_requests
        self.assertLess(avg_time, 0.1)

    def test_concurrent_users_profile_access(self):
        """Тест одночасного доступу багатьох користувачів"""
        # Створюємо багато користувачів
        users = []
        for i in range(10):
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                password='testpass123',
                is_active=True,
                is_verified_email=True
            )
            users.append(user)

        results = []
        threads = []

        def user_activity(user):
            client = Client()
            client.force_login(user)

            user_results = []
            for _ in range(10):
                # GET запит
                response = client.get('/api/user/profile/')
                user_results.append(response.status_code == 200)

                # PATCH запит
                update_data = {'user': {'name': f'Updated{time.time()}'}}
                response = client.patch(
                    '/api/user/profile/',
                    data=json.dumps(update_data),
                    content_type='application/json'
                )
                user_results.append(response.status_code == 200)

            results.extend(user_results)

        # Запускаємо потоки
        for user in users:
            thread = threading.Thread(target=user_activity, args=(user,))
            threads.append(thread)
            thread.start()

        # Чекаємо завершення
        for thread in threads:
            thread.join()

        # Перевірка результатів
        success_rate = sum(results) / len(results)
        self.assertGreaterEqual(success_rate, 0.9)

    def test_memory_usage_under_load(self):
        """Тест використання пам'яті під навантаженням"""
        client = Client()
        client.force_login(self.user)

        # Множинні запити з великими даними
        large_bio = "x" * 1000  # 1KB біографія

        for i in range(50):
            update_data = {
                'profile': {'bio': f'{large_bio}_{i}'}
            }

            response = client.patch(
                '/api/user/profile/',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

        # Перевірка що система все ще відповідає
        response = client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)
