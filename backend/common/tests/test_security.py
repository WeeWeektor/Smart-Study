from django.test import TestCase
from django.http import HttpRequest
from common.utils.language_utils import validate_language, get_language_from_request, parce_accept_language


class TestSecurityValidation(TestCase):
    """Тести безпеки"""

    def test_injection_attempts_in_language(self):
        """Тест SQL injection та XSS спроб"""
        malicious = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "../../../windows/system32",
            "en\x00uk",
            "en\n\ruk",
            "en${IFS}uk"
        ]
        for lang in malicious:
            with self.subTest(lang=lang):
                result = validate_language(lang)
                self.assertEqual(result, 'en')

    def test_very_long_language_values(self):
        """Тест з дуже довгими значеннями"""
        long_lang = 'a' * 1000
        result = validate_language(long_lang)
        self.assertEqual(result, 'en')

    def test_null_bytes_in_language(self):
        """Тест з null bytes"""
        dangerous = ['en\x00', 'uk\x00\x00', '\x00en']
        for lang in dangerous:
            with self.subTest(lang=lang):
                result = validate_language(lang)
                self.assertEqual(result, 'en')

    def test_unicode_attacks(self):
        """Тест з Unicode атаками"""
        unicode_attacks = [
            'en\u202euk',  # Right-to-left override
            'en\ufeffuk',  # Zero width no-break space
            'en\u200buk',  # Zero width space
            '𝕖𝕟',  # Mathematical alphanumeric symbols
        ]
        for lang in unicode_attacks:
            with self.subTest(lang=lang):
                result = validate_language(lang)
                self.assertEqual(result, 'en')

    def test_request_header_injection(self):
        """Тест injection через headers"""
        request = HttpRequest()
        request.META['HTTP_ACCEPT_LANGUAGE'] = 'en\r\nSet-Cookie: evil=true'

        result = get_language_from_request(request)
        self.assertIn(result, ['en', 'uk'])  # Не повинен обробляти injection

    def test_cookie_injection_protection(self):
        """Тест захисту від cookie injection"""
        request = HttpRequest()
        request.COOKIES['django_language'] = 'en; Path=/; HttpOnly; Secure'

        result = get_language_from_request(request)
        self.assertEqual(result, 'en')  # Повинен взяти тільки 'en'
