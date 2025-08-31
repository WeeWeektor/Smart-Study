import time
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.core.cache import cache

User = get_user_model()


class ProfilePerformanceTest(TestCase):
    """Тести продуктивності для профілю"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='perf@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)

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

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    })
    def test_performance_without_cache(self):
        """Тест продуктивності без кешування"""
        cache.clear()

        start_time = time.time()
        response = self.client.get('/api/user/profile/')
        end_time = time.time()

        self.assertEqual(response.status_code, 200)

        request_time = end_time - start_time
        self.assertLess(request_time, 2.0)
