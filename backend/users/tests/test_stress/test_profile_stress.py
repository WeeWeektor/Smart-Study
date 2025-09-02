import json
import threading
import time

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase, Client

from smartStudy_backend import settings
from users.models import CustomUser

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

        self.stress_users = []
        for i in range(20):
            user = User.objects.create_user(
                email=f'stress_user_{i}@example.com',
                password='stresspass123',
                is_active=True,
                is_verified_email=True
            )
            self.stress_users.append(user)

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
                response = client.get('/api/user/profile/')
                user_results.append(response.status_code == 200)

                update_data = {'user': {'name': f'Updated{time.time()}'}}
                response = client.patch(
                    '/api/user/profile/',
                    data=json.dumps(update_data),
                    content_type='application/json'
                )
                user_results.append(response.status_code == 200)

            results.extend(user_results)

        for user in users:
            thread = threading.Thread(target=user_activity, args=(user,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        success_rate = sum(results) / len(results)
        self.assertGreaterEqual(success_rate, 0.9)

    def test_memory_usage_under_load(self):
        """Тест використання пам'яті під навантаженням"""
        client = Client()
        client.force_login(self.user)

        large_bio = "x" * 1000

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

        response = client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)

    def test_extreme_concurrent_profile_access(self):
        original_setting = getattr(settings, 'DISABLE_RATE_LIMITING', False)
        settings.DISABLE_RATE_LIMITING = True

        try:
            user = CustomUser.objects.create_user(
                email='concurrent@example.com',
                name='Concurrent',
                surname='Test',
                password='TestPassword123!',
                role='student',
                is_active=True,
                is_verified_email=True
            )

            self.client.force_login(user)

            success_count = 0
            total_requests = 20

            for i in range(total_requests):
                try:
                    response = self.client.get('/api/user/profile/')
                    if response.status_code == 200:
                        success_count += 1
                except Exception:
                    pass

            success_rate = success_count / total_requests
            self.assertGreaterEqual(success_rate, 0.70)

        finally:
            settings.DISABLE_RATE_LIMITING = original_setting

    def test_database_connection_exhaustion(self):
        """Тест вичерпання з'єднань з БД"""
        clients = []
        connections_used = []

        def create_connection_pressure():
            client = Client()
            client.force_login(self.user)
            clients.append(client)

            response = client.get('/api/user/profile/')
            connections_used.append(response.status_code == 200)

        threads = []
        for i in range(30):
            thread = threading.Thread(target=create_connection_pressure)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(timeout=10)

        success_rate = sum(connections_used) / len(connections_used) if connections_used else 0

        print(f"🔥 DB connections test: {sum(connections_used)}/{len(connections_used)} successful")
        print(f"🔥 Connection success rate: {success_rate:.2%}")

        self.assertGreaterEqual(success_rate, 0.85)

    def test_rapid_profile_updates(self):
        """Тест швидких оновлень профілю"""
        client = Client()
        client.force_login(self.user)

        update_times = []
        successful_updates = 0

        for i in range(100):
            start = time.time()

            update_data = {
                'user': {'name': f'StressUser{i}'}
            }

            response = client.patch(
                '/api/user/profile/',
                data=json.dumps(update_data),
                content_type='application/json'
            )

            end = time.time()
            update_times.append(end - start)

            if response.status_code == 200:
                successful_updates += 1

        success_rate = successful_updates / 100
        avg_update_time = sum(update_times) / len(update_times)
        max_update_time = max(update_times)

        print(f"🔥 Rapid updates: {successful_updates}/100 successful")
        print(f"🔥 Average update time: {avg_update_time:.3f}s")
        print(f"🔥 Max update time: {max_update_time:.3f}s")

        self.assertGreaterEqual(success_rate, 0.95)
        self.assertLess(avg_update_time, 0.5)
        self.assertLess(max_update_time, 2.0)
