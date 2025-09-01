from django.contrib.auth.models import User
from django.test import TransactionTestCase


class AdvancedSecurityTest(TransactionTestCase):
    """Розширені тести безпеки"""

    def test_session_hijacking_protection(self):
        """Захист від session hijacking"""
        # Тест зміни IP адреси в сесії
        user = User.objects.create_user(
            email='session@example.com',
            password='TestPass123!',
            is_verified_email=True
        )

        # Логін з одного IP
        session = self.client.session
        self.client.force_login(user)

        # Симуляція зміни IP
        response = self.client.get('/api/user/profile/',
                                   HTTP_X_FORWARDED_FOR='192.168.1.100')

        # Система повинна вимагати ре-автентифікації
        self.assertIn(response.status_code, [401, 403])

    def test_brute_force_protection(self):
        """Захист від brute force атак"""
        for i in range(10):
            response = self.client.post('/api/auth/login/', {
                'email': 'victim@example.com',
                'password': f'wrong_password_{i}'
            })

        # Останній запит повинен бути заблокований
        self.assertEqual(response.status_code, 429)

    def test_privilege_escalation_protection(self):
        """Захист від privilege escalation"""
        regular_user = User.objects.create_user(
            email='regular@example.com',
            password='test123',
            role='student'
        )

        self.client.force_login(regular_user)

        # Спроба отримати admin права
        response = self.client.patch('/api/user/profile/', {
            'user': {'role': 'admin', 'is_staff': True}
        })

        # Не повинно дозволити зміну ролі
        regular_user.refresh_from_db()
        self.assertEqual(regular_user.role, 'student')
        self.assertFalse(regular_user.is_staff)
