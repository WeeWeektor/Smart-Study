import threading
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model


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

    def test_extreme_concurrent_profile_access(self):
        """Тест екстремального одночасного доступу"""
        results = []
        errors = []

        def stress_profile_request(user_id):
            try:
                client = Client()
                user = User.objects.get(id=user_id)
                client.force_login(user)

                start = time.time()
                response = client.get('/api/user/profile/')
                end = time.time()

                return {
                    'user_id': user_id,
                    'status': response.status_code,
                    'time': end - start,
                    'success': response.status_code == 200
                }
            except Exception as e:
                errors.append(str(e))
                return None

        # 100 одночасних запитів
        user_ids = [user.id for user in self.stress_users[:10]] * 10

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(stress_profile_request, uid) for uid in user_ids]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        # Аналіз результатів
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        success_rate = len(successful) / len(results) if results else 0
        avg_response_time = sum(r['time'] for r in successful) / len(successful) if successful else 0

        print(f"🔥 Extreme concurrent test: {len(successful)}/{len(results)} successful")
        print(f"🔥 Success rate: {success_rate:.2%}")
        print(f"🔥 Average response time: {avg_response_time:.3f}s")
        print(f"🔥 Errors: {len(errors)}")

        # Під extreme навантаженням прийнятний success rate 80%
        self.assertGreaterEqual(success_rate, 0.80)
        self.assertLess(avg_response_time, 2.0)

    def test_database_connection_exhaustion(self):
        """Тест вичерпання з'єднань з БД"""
        clients = []
        connections_used = []

        def create_connection_pressure():
            client = Client()
            client.force_login(self.user)
            clients.append(client)

            # Запит що використовує DB connection
            response = client.get('/api/user/profile/')
            connections_used.append(response.status_code == 200)

        # Створення багатьох одночасних з'єднань
        threads = []
        for i in range(30):
            thread = threading.Thread(target=create_connection_pressure)
            threads.append(thread)
            thread.start()

        # Очікування завершення всіх потоків
        for thread in threads:
            thread.join(timeout=10)

        success_rate = sum(connections_used) / len(connections_used) if connections_used else 0

        print(f"🔥 DB connections test: {sum(connections_used)}/{len(connections_used)} successful")
        print(f"🔥 Connection success rate: {success_rate:.2%}")

        # Більшість з'єднань повинні бути успішними
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
