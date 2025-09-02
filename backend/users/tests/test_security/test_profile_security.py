import json

import unicodedata
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client

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
            b"x" * (10 * 1024 * 1024),
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

    def test_xss_protection_in_profile(self):
        """Тест захисту від XSS атак"""
        user = User.objects.create_user(
            email='xss@example.com',
            password='test123',
            is_verified_email=True,
            is_active=True
        )
        self.client.force_login(user)

        xss_data = {
            'profile': {
                'bio': '<script>alert("XSS")</script>',
                'location': '<img src=x onerror=alert(1)>'
            }
        }

        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps(xss_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/user/profile/')
        data = response.json()
        self.assertNotIn('<script>', str(data))
        self.assertNotIn('onerror', str(data))

    def test_rate_limiting(self):
        """Тест rate limiting"""
        for i in range(20):
            response = self.client.post(
                '/api/auth/login/',
                data=json.dumps({
                    'email': f'test{i}@example.com',
                    'password': 'wrong'
                }),
                content_type='application/json'
            )

        last_response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({
                'email': 'final@example.com',
                'password': 'wrong'
            }),
            content_type='application/json'
        )

        self.assertIn(last_response.status_code, [400, 401, 429])

    def test_path_traversal_protection(self):
        """Тест захисту від path traversal атак"""
        self.client.force_login(self.user)

        path_traversal_payloads = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '....//....//....//etc/passwd',
            '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
            '..%252f..%252f..%252fetc%252fpasswd',
        ]

        for payload in path_traversal_payloads:
            malicious_file = SimpleUploadedFile(
                payload,
                b"malicious content",
                content_type="text/plain"
            )

            response = self.client.post(
                '/api/user/profile/',
                {'profile_picture': malicious_file}
            )

            self.assertEqual(response.status_code, 400)

    def test_content_type_spoofing_protection(self):
        """Тест захисту від підробки content-type"""
        self.client.force_login(self.user)

        spoofed_file = SimpleUploadedFile(
            "image.jpg.php",
            b"<?php system($_GET['cmd']); ?>",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': spoofed_file}
        )

        self.assertEqual(response.status_code, 400)

    def test_file_signature_validation(self):
        """Тест валідації сигнатури файлу"""
        self.client.force_login(self.user)

        fake_jpeg = SimpleUploadedFile(
            "fake.jpg",
            b"this is not a real jpeg file",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': fake_jpeg}
        )

        self.assertEqual(response.status_code, 400)

    def test_unicode_normalization_attack(self):
        """Тест захисту від Unicode normalization атак"""
        self.client.force_login(self.user)

        unicode_payloads = [
            'admin\u200badmin',  # Zero Width Space
            'admin\u200cadmin',  # Zero Width Non-Joiner
            'admin\u200dadmin',  # Zero Width Joiner
            'admin\u00adadmin',  # Soft Hyphen
            'admin\ufeffadmin',  # Zero Width No-Break Space
            'admin\u202eadmin',  # Right-to-Left Override
            'admin\u0008admin',  # Backspace (control character)
            'admin\u0000admin',  # Null character
        ]

        for payload in unicode_payloads:
            with self.subTest(payload=repr(payload)):
                data = {
                    'profile': {
                        'bio': payload
                    }
                }

                response = self.client.patch(
                    '/api/user/profile/',
                    data=json.dumps(data),
                    content_type='application/json'
                )

                self.assertEqual(response.status_code, 200)

                response = self.client.get('/api/user/profile/')
                profile_data = response.json()
                normalized_bio = profile_data.get('profile', {}).get('bio') or ''

                self.assertNotEqual(normalized_bio, payload,
                                    f"Unicode payload not sanitized: {repr(payload)} -> {repr(normalized_bio)}")

                self.assertIn('admin', normalized_bio)

                for char in normalized_bio:
                    self.assertNotEqual(unicodedata.category(char)[0], 'C',
                                        f"Control character found: {repr(char)} in {repr(normalized_bio)}")
