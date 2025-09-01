from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class SecurityIntegrationTest(TransactionTestCase):
    """Комплексні тести безпеки"""

    def test_sql_injection_protection(self):
        """SQL injection захист"""
        user = User.objects.create_user(
            email='security@example.com',
            password='TestPass123!',
            is_verified_email=True,
            is_active=True
        )
        self.client.force_login(user)

        malicious_data = {
            'user': {
                'name': "'; DROP TABLE users; --"
            }
        }

        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps(malicious_data),
            content_type='application/json'
        )

        # Не повинен падати, дані повинні санітизуватись
        self.assertIn(response.status_code, [200, 400])

        # Перевірка що БД не пошкоджена
        self.assertTrue(User.objects.filter(id=user.id).exists())

    def test_comprehensive_xss_protection(self):
        """Комплексний XSS захист"""
        user = User.objects.create_user(
            email='xss@example.com',
            password='TestPass123!',
            is_verified_email=True,
            is_active=True
        )
        self.client.force_login(user)

        xss_vectors = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            'javascript:alert("XSS")',
            '<svg onload=alert("XSS")>',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>'
        ]

        for xss_payload in xss_vectors:
            response = self.client.patch(
                '/api/user/profile/',
                data=json.dumps({
                    'profile': {'bio': xss_payload}
                }),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

            # Перевірка санітизації
            response = self.client.get('/api/user/profile/')
            data = response.json()
            profile_content = str(data.get('profile', {}))

            # Небезпечні теги повинні бути видалені
            self.assertNotIn('<script>', profile_content)
            self.assertNotIn('onerror', profile_content)
            self.assertNotIn('javascript:', profile_content)
            self.assertNotIn('<svg', profile_content)
            self.assertNotIn('<iframe', profile_content)
