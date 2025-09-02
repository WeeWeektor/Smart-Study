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

        response1 = self.client.get(reverse('user_urls:profile'))
        self.assertEqual(response1.status_code, 200)

        cache_key = f"user_profile_{self.user.id}"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)

        response2 = self.client.get(reverse('user_urls:profile'))
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response1.content, response2.content)

        initial_cached_bio = cached_data.get('profile', {}).get('bio')

        update_data = {
            'profile': {'bio': 'New bio for cache test'}
        }

        response3 = self.client.patch(
            reverse('user_urls:profile'),
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response3.status_code, 200)

        cached_data_after_update = cache.get(cache_key)
        self.assertIsNotNone(cached_data_after_update)

        updated_bio = cached_data_after_update.get('profile', {}).get('bio')
        self.assertEqual(updated_bio, 'New bio for cache test')
        self.assertNotEqual(initial_cached_bio, updated_bio)

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

        response1 = self.client.get(reverse('user_urls:profile'))
        self.assertEqual(response1.status_code, 200)

        cache_key = f"user_profile_{self.user.id}"
        initial_cached_data = cache.get(cache_key)
        self.assertIsNotNone(initial_cached_data)

        user_update_data = {
            'user': {'name': 'Updated Name'}
        }

        response2 = self.client.patch(
            reverse('user_urls:profile'),
            data=json.dumps(user_update_data),
            content_type='application/json'
        )

        self.assertEqual(response2.status_code, 200)

        updated_cached_data = cache.get(cache_key)
        self.assertIsNotNone(updated_cached_data)

        self.assertNotEqual(
            initial_cached_data['user']['name'],
            updated_cached_data['user']['name']
        )
        self.assertEqual(updated_cached_data['user']['name'], 'Updated Name')

    def test_user_existence_cache(self):
        """Кеш перевірки існування користувача"""

        async def test_flow():
            email = 'cache@example.com'

            exists1 = await get_user_existence_cache(email)
            self.assertTrue(exists1['exists'])

            cache_key = f"user_exists_{hash(email)}"
            cached_result = cache.get(cache_key)
            self.assertIsNotNone(cached_result)

            exists2 = await get_user_existence_cache(email)
            self.assertTrue(exists2['exists'])

        asyncio.run(test_flow())

    def test_cache_performance_integration(self):
        """Тест продуктивності кешування"""
        import time

        async def test_flow():
            email = self.user.email

            start_time = time.time()
            await get_user_existence_cache(f"new_{email}")
            first_call_time = time.time() - start_time

            start_time = time.time()
            await get_user_existence_cache(f"new_{email}")
            second_call_time = time.time() - start_time

            self.assertLessEqual(second_call_time, first_call_time * 2)

        asyncio.run(test_flow())
