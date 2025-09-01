import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor

from django.test import TestCase, override_settings, TransactionTestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.core.cache import cache

from users.services.profile_cache_service import get_cached_profile

User = get_user_model()


class ProfilePerformanceTest(TestCase):
    """Тести продуктивності для профілю"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='perf@example.com',
            password='testpass123',
            is_active=True,
            is_verified_email=True,
        )
        self.client.force_login(self.user)

        # Створення тестових користувачів для bulk операцій
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                email=f'perf_user_{i}@example.com',
                password='testpass123',
                is_active=True,
                is_verified_email=True,
            )
            self.users.append(user)

    def test_profile_get_performance(self):
        """Тест продуктивності отримання профілю"""
        start_time = time.time()

        for _ in range(10):
            response = self.client.get('/api/user/profile/')
            self.assertEqual(response.status_code, 200)

        end_time = time.time()
        avg_time = (end_time - start_time) / 10

        self.assertLess(avg_time, 1.0)

    def test_cache_effectiveness(self):
        """Тест ефективності кешування"""
        start_time = time.time()
        response1 = self.client.get('/api/user/profile/')
        first_request_time = time.time() - start_time

        start_time = time.time()
        response2 = self.client.get('/api/user/profile/')
        second_request_time = time.time() - start_time

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

        self.assertLess(second_request_time, first_request_time)

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        },
        SESSION_ENGINE='django.contrib.sessions.backends.db'
    )
    def test_performance_without_cache(self):
        """Тест продуктивності без кешування"""
        user = User.objects.create_user(
            email='no-cache@example.com',
            password='testpass123',
            is_active=True,
            is_verified_email=True,
        )
        client = Client()
        client.force_login(user)

        start_time = time.time()
        response = client.get('/api/user/profile/')
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        request_time = end_time - start_time
        self.assertLess(request_time, 2.0)

    def test_bulk_operations_performance(self):
        """Тест продуктивності bulk операцій"""
        # 1. Bulk створення користувачів
        start = time.time()

        users_to_create = [
            User(
                email=f'bulk{i}@example.com',
                password='hashedpass123',
                name=f'User{i}',
                surname=f'Surname{i}',
                role='student'
            ) for i in range(100, 200)
        ]

        User.objects.bulk_create(users_to_create, batch_size=50)
        creation_time = time.time() - start

        print(f"📊 Bulk creation of 100 users: {creation_time:.3f}s")
        self.assertLess(creation_time, 2.0, "Bulk creation should be under 2 seconds")

        # 2. Bulk оновлення
        created_users = User.objects.filter(email__startswith='bulk')

        start = time.time()
        for user in created_users:
            user.is_active = True

        User.objects.bulk_update(created_users, ['is_active'], batch_size=50)
        update_time = time.time() - start

        print(f"📊 Bulk update of 100 users: {update_time:.3f}s")
        self.assertLess(update_time, 1.5, "Bulk update should be under 1.5 seconds")

        # 3. Bulk видалення
        start = time.time()
        deleted_count = User.objects.filter(email__startswith='bulk').delete()[0]
        deletion_time = time.time() - start

        print(f"📊 Bulk deletion of {deleted_count} users: {deletion_time:.3f}s")
        self.assertLess(deletion_time, 1.0, "Bulk deletion should be under 1 second")

    def test_concurrent_profile_access(self):
        """Тест одночасного доступу до профілів"""
        results = []

        def profile_request(user_index):
            start = time.time()
            client = Client()
            client.force_login(self.users[user_index % len(self.users)])

            response = client.get('/api/user/profile/')
            end = time.time()

            results.append({
                'status': response.status_code,
                'time': end - start,
                'user_index': user_index
            })

        # Одночасні запити від 20 користувачів
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(profile_request, i) for i in range(20)]
            for future in futures:
                future.result()

        # Аналіз результатів
        successful_requests = [r for r in results if r['status'] == 200]
        avg_time = sum(r['time'] for r in successful_requests) / len(successful_requests)
        max_time = max(r['time'] for r in successful_requests)

        print(f"📊 Concurrent requests - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")

        self.assertEqual(len(successful_requests), 20, "All requests should succeed")
        self.assertLess(avg_time, 1.0, "Average response time should be under 1s")
        self.assertLess(max_time, 3.0, "Max response time should be under 3s")

    def test_database_query_optimization(self):
        """Тест оптимізації запитів до БД"""
        with self.assertNumQueries(5):  # Максимум 5 запитів
            response = self.client.get('/api/user/profile/')
            self.assertEqual(response.status_code, 200)

    def test_memory_usage_profile_operations(self):
        """Тест використання пам'яті під час операцій з профілем"""
        import tracemalloc

        tracemalloc.start()

        # Операції з профілем
        for i in range(50):
            self.client.get('/api/user/profile/')

            if i % 10 == 0:
                update_data = {
                    'user': {'name': f'Updated Name {i}'}
                }
                self.client.patch(
                    '/api/user/profile/',
                    data=json.dumps(update_data),
                    content_type='application/json'
                )

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024
        print(f"📊 Peak memory usage: {peak_mb:.2f} MB")

        # Пікове використання не повинно перевищувати 100MB
        self.assertLess(peak_mb, 100, "Peak memory usage should be under 100MB")

    def test_cache_performance_under_load(self):
        """Тест продуктивності кешу під навантаженням"""

        async def test_flow():
            # Прогрів кешу
            for user in self.users[:5]:
                await get_cached_profile(user)

            # Вимірювання часу з кешем
            start = time.time()
            for user in self.users[:5]:
                await get_cached_profile(user)
            cached_time = time.time() - start

            # Очищення кешу
            cache.clear()

            # Вимірювання часу без кешу
            start = time.time()
            for user in self.users[:5]:
                await get_cached_profile(user)
            uncached_time = time.time() - start

            print(f"📊 Cache performance - Cached: {cached_time:.3f}s, Uncached: {uncached_time:.3f}s")

            # Кеш повинен бути швидшим
            self.assertLess(cached_time, uncached_time)

        asyncio.run(test_flow())
