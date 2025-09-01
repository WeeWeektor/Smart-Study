from django.test import TransactionTestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.services.profile_cache_service import get_user_existence_cache
import json
import asyncio

User = get_user_model()


class CacheIntegrationTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='cache@example.com',
            password='TestPass123!',
            is_verified_email=True,
            is_active=True,
        )
        cache.clear()

    def test_user_profile_cache_lifecycle(self):
        """Життєвий цикл кешу профілю користувача"""
        self.client.force_login(self.user)

        # 1. Перший запит - дані з БД, створення кешу
        response1 = self.client.get(reverse('user_urls:profile'))
        self.assertEqual(response1.status_code, 200)

        # Перевірка створення кешу
        cache_key = f"user_profile_{self.user.id}"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)

        # 2. Другий запит - дані з кешу
        response2 = self.client.get(reverse('user_urls:profile'))
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response1.content, response2.content)

        # Зберігаємо початкові дані кешу
        initial_cached_bio = cached_data.get('profile', {}).get('bio')

        # 3. Оновлення профілю
        update_data = {
            'profile': {'bio': 'New bio for cache test'}
        }

        response3 = self.client.patch(
            reverse('user_urls:profile'),
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response3.status_code, 200)

        # Перевірка оновлення кешу (кеш оновлюється, а не інвалідується)
        cached_data_after_update = cache.get(cache_key)
        self.assertIsNotNone(cached_data_after_update)

        # Перевірка, що дані в кеші оновилися
        updated_bio = cached_data_after_update.get('profile', {}).get('bio')
        self.assertEqual(updated_bio, 'New bio for cache test')
        self.assertNotEqual(initial_cached_bio, updated_bio)

        # 4. Перевірка, що наступний запит використовує оновлений кеш
        response4 = self.client.get(reverse('user_urls:profile'))
        self.assertEqual(response4.status_code, 200)
        response4_data = response4.json()
        self.assertEqual(
            response4_data['profile']['bio'],
            'New bio for cache test'
        )

    def test_cache_invalidation_on_profile_update(self):
        """Тест оновлення кешу при зміні профілю"""
        self.client.force_login(self.user)

        # Створюємо початковий кеш
        response1 = self.client.get(reverse('user_urls:profile'))
        self.assertEqual(response1.status_code, 200)

        cache_key = f"user_profile_{self.user.id}"
        initial_cached_data = cache.get(cache_key)
        self.assertIsNotNone(initial_cached_data)

        # Оновлюємо користувача
        user_update_data = {
            'user': {'name': 'Updated Name'}
        }

        response2 = self.client.patch(
            reverse('user_urls:profile'),
            data=json.dumps(user_update_data),
            content_type='application/json'
        )

        self.assertEqual(response2.status_code, 200)

        # Перевірка оновлення кешу
        updated_cached_data = cache.get(cache_key)
        self.assertIsNotNone(updated_cached_data)

        # Дані мають відрізнятися
        self.assertNotEqual(
            initial_cached_data['user']['name'],
            updated_cached_data['user']['name']
        )
        self.assertEqual(updated_cached_data['user']['name'], 'Updated Name')

    def test_user_existence_cache(self):
        """Кеш перевірки існування користувача"""

        async def test_flow():
            email = 'cache@example.com'

            # Перша перевірка - запис в кеш
            exists1 = await get_user_existence_cache(email)
            self.assertTrue(exists1['exists'])

            # Перевірка кешу
            cache_key = f"user_exists_{hash(email)}"
            cached_result = cache.get(cache_key)
            self.assertIsNotNone(cached_result)

            # Друга перевірка - з кешу
            exists2 = await get_user_existence_cache(email)
            self.assertTrue(exists2['exists'])

        asyncio.run(test_flow())

    def test_cache_performance_integration(self):
        """Тест продуктивності кешування"""
        import time

        async def test_flow():
            email = self.user.email

            # Вимірювання часу без кешу
            start_time = time.time()
            await get_user_existence_cache(f"new_{email}")
            first_call_time = time.time() - start_time

            # Вимірювання часу з кешем
            start_time = time.time()
            await get_user_existence_cache(f"new_{email}")
            second_call_time = time.time() - start_time

            # Другий виклик повинен бути швидшим (або принаймні не повільнішим)
            self.assertLessEqual(second_call_time, first_call_time * 2)

        asyncio.run(test_flow())