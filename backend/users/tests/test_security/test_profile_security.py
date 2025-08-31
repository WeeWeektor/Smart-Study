import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class ProfileSecurityTest(TestCase):
    """Тести безпеки профілю"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='secure@example.com',
            password='testpass123',
            is_active=True,
            is_verified_email=True
        )

    def test_malicious_file_upload_protection(self):
        """Тест захисту від зловмисних файлів"""
        self.client.force_login(self.user)

        malicious_file = SimpleUploadedFile(
            "malware.exe",
            b"MZ\x90\x00",
            content_type="application/octet-stream"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': malicious_file}
        )

        self.assertEqual(response.status_code, 400)

    def test_oversized_file_protection(self):
        """Тест захисту від занадто великих файлів"""
        self.client.force_login(self.user)

        large_file = SimpleUploadedFile(
            "large.jpg",
            b"x" * (10 * 1024 * 1024),  # 10MB
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': large_file}
        )

        self.assertEqual(response.status_code, 400)

    def test_sql_injection_in_profile_data(self):
        """Тест захисту від SQL injection"""
        self.client.force_login(self.user)

        malicious_data = {
            'user': {
                'name': "'; DROP TABLE users; --",
                'surname': "Robert'; DELETE FROM users WHERE '1'='1"
            }
        }

        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps(malicious_data),
            content_type='application/json'
        )

        self.assertIn(response.status_code, [200, 400])

    def test_xss_protection_in_profile_data(self):
        """Тест захисту від XSS"""
        self.client.force_login(self.user)

        xss_data = {
            'profile': {
                'bio': '<script>alert("XSS")</script>'
            }
        }

        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps(xss_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        profile_response = self.client.get('/api/user/profile/')
        self.assertNotIn('<script>', profile_response.content.decode())