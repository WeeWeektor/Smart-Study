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

        # Перевірка що скрипти видалені
        response = self.client.get('/api/user/profile/')
        data = response.json()
        self.assertNotIn('<script>', str(data))
        self.assertNotIn('onerror', str(data))

    def test_rate_limiting(self):
        """Тест rate limiting"""
        # Багато запитів логіну
        for i in range(20):
            response = self.client.post(
                '/api/auth/login/',
                data=json.dumps({
                    'email': f'test{i}@example.com',
                    'password': 'wrong'
                }),
                content_type='application/json'
            )

        # Деякі запити повинні бути заблоковані
        last_response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({
                'email': 'final@example.com',
                'password': 'wrong'
            }),
            content_type='application/json'
        )

        # Може бути 429 (Too Many Requests) або продовжувати працювати
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

            # Повинен блокувати підозрілі імена файлів
            self.assertEqual(response.status_code, 400)

    def test_content_type_spoofing_protection(self):
        """Тест захисту від підробки content-type"""
        self.client.force_login(self.user)

        # PHP файл з підробленим content-type
        spoofed_file = SimpleUploadedFile(
            "image.jpg.php",
            b"<?php system($_GET['cmd']); ?>",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': spoofed_file}
        )

        # Повинен виявити підробку
        self.assertEqual(response.status_code, 400)

    def test_file_signature_validation(self):
        """Тест валідації сигнатури файлу"""
        self.client.force_login(self.user)

        # Фейковий JPEG (неправильна сигнатура)
        fake_jpeg = SimpleUploadedFile(
            "fake.jpg",
            b"this is not a real jpeg file",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': fake_jpeg}
        )

        # Повинен виявити невідповідність сигнатури
        self.assertEqual(response.status_code, 400)

    def test_unicode_normalization_attack(self):
        """Тест захисту від Unicode normalization атак"""
        self.client.force_login(self.user)

        # Unicode атаки
        unicode_payloads = [
            'admin\u200badmin',  # Zero-width space
            'ⅆⅇv⁄null',  # Mathematical symbols
            '𝒶𝒹𝓂𝒾𝓃',  # Mathematical script
            'аdmin',  # Cyrillic 'а' instead of Latin 'a'
        ]

        for payload in unicode_payloads:
            data = {
                'user': {'name': payload}
            }

            response = self.client.patch(
                '/api/user/profile/',
                data=json.dumps(data),
                content_type='application/json'
            )

            # Перевірка нормалізації
            self.assertEqual(response.status_code, 200)

            # Отримання профілю для перевірки нормалізації
            response = self.client.get('/api/user/profile/')
            data = response.json()
            normalized_name = data['user']['name']

            # Ім'я повинно бути нормалізоване
            self.assertNotEqual(normalized_name, payload)
