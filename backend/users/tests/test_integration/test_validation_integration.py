from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from users.services.profile_update_service import update_user_data, update_user_profile
from users.models import UserProfile
from asgiref.sync import sync_to_async
import asyncio

User = get_user_model()


class ValidationIntegrationTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='Test',
            surname='User',
            email='validation@example.com',
            password='TestPass123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )
        UserProfile.objects.get_or_create(user=self.user)

    def test_phone_validation_integration(self):
        """Інтеграція валідації телефону"""

        async def test_flow():
            # Валідний номер
            valid_data = {'phone_number': '+380501234567'}
            await update_user_data(self.user, valid_data)
            await self.user.arefresh_from_db()
            self.assertEqual(self.user.phone_number, '+380501234567')

            # Невалідний номер
            invalid_data = {'phone_number': 'invalid_phone'}
            with self.assertRaises((ValidationError, ValueError)):
                await update_user_data(self.user, invalid_data)

            # Очищення номера
            clear_data = {'phone_number': None}
            await update_user_data(self.user, clear_data)
            await self.user.arefresh_from_db()
            self.assertIsNone(self.user.phone_number)

        asyncio.run(test_flow())

    def test_email_validation_integration(self):
        """Інтеграція валідації email"""

        async def test_flow():
            original_email = self.user.email
            invalid_data = {'email': 'invalid-email'}

            try:
                await update_user_data(self.user, invalid_data)
                await self.user.arefresh_from_db()
                self.assertEqual(self.user.email, original_email)
            except (ValidationError, ValueError):
                pass

            # Дублікат email - використовуємо sync_to_async
            duplicate_user = await sync_to_async(User.objects.create_user)(
                name='Duplicate',
                surname='User',
                email='duplicate@example.com',
                password='TestPass123!',
                role='student'
            )

            duplicate_data = {'email': 'duplicate@example.com'}

            try:
                await update_user_data(self.user, duplicate_data)
                await self.user.arefresh_from_db()
                self.assertEqual(self.user.email, original_email)
            except (ValidationError, ValueError):
                pass

        asyncio.run(test_flow())

    def test_data_sanitization_integration(self):
        """Інтеграція санітизації даних"""

        async def test_flow():
            unsafe_data = {
                'bio': '<script>alert("XSS")</script>Safe content',
                'location': '<img src=x onerror=alert("XSS")>Kyiv',
                'organization': '<b>Company</b> Name'
            }

            await update_user_profile(self.user, unsafe_data)

            profile = await sync_to_async(UserProfile.objects.get)(user=self.user)

            self.assertNotIn('<script>', profile.bio)
            self.assertNotIn('onerror', profile.location)
            self.assertIn('Safe content', profile.bio)
            self.assertIn('Kyiv', profile.location)
            self.assertIn('Company', profile.organization)

        asyncio.run(test_flow())

    def test_role_validation_integration(self):
        """Інтеграція валідації ролі"""

        async def test_flow():
            original_role = self.user.role  # 'student'

            # Невалідна роль
            invalid_data = {'role': 'invalid_role'}

            try:
                await update_user_data(self.user, invalid_data)
                await self.user.arefresh_from_db()
                # Роль не повинна змінитися при невалідному значенні
                self.assertEqual(self.user.role, original_role)
            except (ValidationError, ValueError):
                pass

            # Тестуємо що валідна роль теж не змінюється
            # (якщо система не дозволяє змінювати ролі через update_user_data)
            valid_data = {'role': 'teacher'}
            await update_user_data(self.user, valid_data)
            await self.user.arefresh_from_db()

            # Перевіряємо, чи роль залишилася незмінною
            # Це може бути очікуваною поведінкою з міркувань безпеки
            self.assertEqual(self.user.role, original_role)

        asyncio.run(test_flow())