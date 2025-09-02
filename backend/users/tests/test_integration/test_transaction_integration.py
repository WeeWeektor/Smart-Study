from django.test import TransactionTestCase
from django.db import transaction
from django.contrib.auth import get_user_model
from users.services.profile_update_service import update_user_data
import asyncio

User = get_user_model()


class TransactionIntegrationTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='transaction@example.com',
            password='TestPass123!',
            is_verified_email=True
        )

    def test_atomic_profile_update(self):
        """Тест атомарного оновлення профілю"""

        async def test_flow():
            try:
                async with transaction.atomic():
                    await update_user_data(self.user, {'name': 'Test'})

                    await update_user_data(self.user, {'email': 'invalid-email'})

            except Exception:
                pass

            await self.user.arefresh_from_db()
            self.assertNotEqual(self.user.name, 'Test')

        asyncio.run(test_flow())

    def test_concurrent_user_updates(self):
        """Тест конкурентних оновлень"""
        import threading

        results = []

        def update_user(suffix):
            try:
                from django.db import connection
                connection.ensure_connection()

                async def update():
                    await update_user_data(self.user, {'name': f'User_{suffix}'})

                asyncio.run(update())
                results.append(f'User_{suffix}')
            except Exception as e:
                results.append(f'Error_{suffix}')

        threads = [threading.Thread(target=update_user, args=(i,)) for i in range(3)]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertTrue(any('User_' in result for result in results))
