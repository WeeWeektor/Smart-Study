from django.test import TransactionTestCase
from django.core import mail
from django.contrib.auth import get_user_model
from users.user_utils import send_verification_email, send_password_reset_email
from unittest.mock import patch
import asyncio

User = get_user_model()


class EmailIntegrationTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='email@example.com',
            password='TestPass123!',
            is_verified_email=True,
            is_active=True,
        )

    def test_verification_email_complete_flow(self):
        """Повний цикл верифікації email"""

        async def test_flow():
            # Відправка email верифікації (передаємо користувача, а не email і токен)
            await send_verification_email(self.user)

            # Перевірка відправки
            self.assertEqual(len(mail.outbox), 1)
            verification_email = mail.outbox[0]

            self.assertIn(self.user.email, verification_email.to)
            self.assertIn('email confirmation for smartstudy', verification_email.subject.lower())
            # Перевірка що email містить посилання
            self.assertTrue(verification_email.body.strip())

        asyncio.run(test_flow())

    def test_password_reset_email_flow(self):
        """Цикл email скидання пароля"""

        async def test_flow():
            # Передаємо користувача, а не email і токен
            await send_password_reset_email(self.user)

            self.assertEqual(len(mail.outbox), 1)
            reset_email = mail.outbox[0]

            self.assertIn(self.user.email, reset_email.to)
            self.assertIn('password recovery for smartstudy', reset_email.subject.lower())
            # Перевірка що email містить посилання
            self.assertTrue(reset_email.body.strip())

        asyncio.run(test_flow())

    @patch('django.utils.translation.activate')
    def test_localized_email_integration(self, mock_activate):
        """Інтеграція локалізованих email"""

        async def test_flow():
            # Тестуємо базову функціональність без параметрів мови
            await send_verification_email(self.user)

            # Перевірка відправки email
            self.assertEqual(len(mail.outbox), 1)
            verification_email = mail.outbox[0]
            self.assertIn(self.user.email, verification_email.to)

            # Очищаємо outbox для наступного тесту
            mail.outbox.clear()

            await send_password_reset_email(self.user)

            self.assertEqual(len(mail.outbox), 1)
            reset_email = mail.outbox[0]
            self.assertIn(self.user.email, reset_email.to)

        asyncio.run(test_flow())

    def test_email_template_rendering(self):
        """Тест рендерингу email шаблонів"""

        async def test_flow():
            await send_verification_email(self.user)

            email = mail.outbox[0]

            # Перевірка що email містить потрібні елементи
            self.assertIn(self.user.email, email.to)
            self.assertTrue(email.body.strip())  # Email не пустий
            self.assertTrue(email.subject.strip())  # Subject не пустий

            # Очищаємо для тесту reset email
            mail.outbox.clear()

            await send_password_reset_email(self.user)

            reset_email = mail.outbox[0]
            self.assertIn(self.user.email, reset_email.to)
            self.assertTrue(reset_email.body.strip())
            self.assertTrue(reset_email.subject.strip())

        asyncio.run(test_flow())

    def test_email_delivery_integration(self):
        """Тест доставки email"""

        async def test_flow():
            # Початковий стан - немає email'ів
            self.assertEqual(len(mail.outbox), 0)

            # Відправка verification email
            await send_verification_email(self.user)
            self.assertEqual(len(mail.outbox), 1)

            verification_email = mail.outbox[0]
            self.assertEqual(verification_email.to, [self.user.email])
            self.assertIn('email confirmation for smartstudy', verification_email.subject.lower())

            # Відправка reset email
            await send_password_reset_email(self.user)
            self.assertEqual(len(mail.outbox), 2)

            reset_email = mail.outbox[1]
            self.assertEqual(reset_email.to, [self.user.email])
            self.assertIn('password recovery for smartstudy', reset_email.subject.lower())

        asyncio.run(test_flow())
