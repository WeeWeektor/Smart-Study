from django.test import TestCase
from unittest.mock import patch
from users.utils.email_templates import (
    get_verification_email_html,
    get_verification_email_plain,
    get_password_reset_email_html,
    get_password_reset_email_plain
)
import re


class TestEmailTemplates(TestCase):
    def setUp(self):
        self.greeting = "Hello John Doe"
        self.activation_url = "https://example.com/activate/token123"
        self.reset_url = "https://example.com/reset/token456"

    def test_get_verification_email_html_basic(self):
        """Тест HTML шаблону для верифікації email"""
        result = get_verification_email_html(self.greeting, self.activation_url)

        self.assertIsInstance(result, str)
        self.assertIn('<html>', result)
        self.assertIn('<body', result)
        self.assertIn('</html>', result)
        self.assertIn(self.greeting, result)
        self.assertIn(self.activation_url, result)

    def test_get_verification_email_html_contains_required_elements(self):
        """Тест що HTML верифікації містить необхідні елементи"""
        result = get_verification_email_html(self.greeting, self.activation_url)

        self.assertIn('<h2 style="color: #4a4a4a;">', result)
        self.assertIn('<a href="', result)
        self.assertIn('background-color: #4CAF50', result)
        self.assertIn('max-width: 600px', result)
        self.assertIn('font-family: Arial', result)

    @patch('users.utils.email_templates.gettext')
    def test_get_verification_email_html_gettext_calls(self, mock_gettext):
        """Тест викликів gettext у HTML верифікації"""
        mock_gettext.side_effect = lambda x: x

        get_verification_email_html(self.greeting, self.activation_url)

        expected_calls = [
            'Thank you for registering with SmartStudy!',
            'To complete your registration and activate your account, please confirm your email address.',
            'Confirm email',
            'If you have not registered with SmartStudy, please disregard this letter.',
            'Sincerely,',
            'The SmartStudy team'
        ]

        for expected_text in expected_calls:
            mock_gettext.assert_any_call(expected_text)

    def test_get_verification_email_plain_basic(self):
        """Тест звичайного текстового шаблону для верифікації email"""
        result = get_verification_email_plain(self.greeting, self.activation_url)

        self.assertIsInstance(result, str)
        self.assertIn(self.greeting, result)
        self.assertIn(self.activation_url, result)
        self.assertNotIn('<html>', result)
        self.assertNotIn('<body>', result)

    @patch('users.utils.email_templates.gettext')
    def test_get_verification_email_plain_gettext_calls(self, mock_gettext):
        """Тест викликів gettext у звичайному тексті верифікації"""
        mock_gettext.side_effect = lambda x: x

        get_verification_email_plain(self.greeting, self.activation_url)

        expected_calls = [
            'Thank you for registering with SmartStudy!',
            'To complete your registration and activate your account, please confirm your email address by clicking on the link:',
            'If you have not registered with SmartStudy, please disregard this letter.',
            'Sincerely,',
            'The SmartStudy Team'
        ]

        for expected_text in expected_calls:
            mock_gettext.assert_any_call(expected_text)

    def test_get_password_reset_email_html_basic(self):
        """Тест HTML шаблону для скидання паролю"""
        result = get_password_reset_email_html(self.greeting, self.reset_url)

        self.assertIsInstance(result, str)
        self.assertIn('<html>', result)
        self.assertIn('<body', result)
        self.assertIn('</html>', result)
        self.assertIn(self.greeting, result)
        self.assertIn(self.reset_url, result)

    def test_get_password_reset_email_html_contains_required_elements(self):
        """Тест що HTML скидання паролю містить необхідні елементи"""
        result = get_password_reset_email_html(self.greeting, self.reset_url)

        self.assertIn('<h2 style="color: #4a4a4a;">', result)
        self.assertIn('<a href="', result)
        self.assertIn('background-color: #4CAF50', result)
        self.assertIn('max-width: 600px', result)
        self.assertIn('font-family: Arial', result)

    @patch('users.utils.email_templates.gettext')
    def test_get_password_reset_email_html_gettext_calls(self, mock_gettext):
        """Тест викликів gettext у HTML скидання паролю"""
        mock_gettext.side_effect = lambda x: x

        get_password_reset_email_html(self.greeting, self.reset_url)

        expected_calls = [
            'You have received this letter because a request has been made to reset the password for your SmartStudy account.',
            'To reset your password, please follow the link below:',
            'Reset password',
            'If you did not request a password reset, please ignore this email.',
            'Sincerely,',
            'The SmartStudy team'
        ]

        for expected_text in expected_calls:
            mock_gettext.assert_any_call(expected_text)

    def test_get_password_reset_email_plain_basic(self):
        """Тест звичайного текстового шаблону для скидання паролю"""
        result = get_password_reset_email_plain(self.greeting, self.reset_url)

        self.assertIsInstance(result, str)
        self.assertIn(self.greeting, result)
        self.assertIn(self.reset_url, result)
        self.assertNotIn('<html>', result)
        self.assertNotIn('<body>', result)

    @patch('users.utils.email_templates.gettext')
    def test_get_password_reset_email_plain_gettext_calls(self, mock_gettext):
        """Тест викликів gettext у звичайному тексті скидання паролю"""
        mock_gettext.side_effect = lambda x: x

        get_password_reset_email_plain(self.greeting, self.reset_url)

        expected_calls = [
            'You have received this letter because a request has been made to reset the password for your SmartStudy account.',
            'To reset your password, please follow this link:',
            'If you did not request a password reset, please ignore this email.',
            'Sincerely,',
            'The SmartStudy Team'
        ]

        for expected_text in expected_calls:
            mock_gettext.assert_any_call(expected_text)

    def test_verification_html_with_special_characters(self):
        """Тест HTML верифікації зі спеціальними символами"""
        special_greeting = "Hello <John> & 'Doe'"
        special_url = "https://example.com/activate?token=abc&user=123"

        result = get_verification_email_html(special_greeting, special_url)

        self.assertIn(special_greeting, result)
        self.assertIn(special_url, result)

    def test_verification_plain_with_special_characters(self):
        """Тест звичайного тексту верифікації зі спеціальними символами"""
        special_greeting = "Hello <John> & 'Doe'"
        special_url = "https://example.com/activate?token=abc&user=123"

        result = get_verification_email_plain(special_greeting, special_url)

        self.assertIn(special_greeting, result)
        self.assertIn(special_url, result)

    def test_password_reset_html_with_special_characters(self):
        """Тест HTML скидання паролю зі спеціальними символами"""
        special_greeting = "Hello <Admin> & 'User'"
        special_url = "https://example.com/reset?token=xyz&id=456"

        result = get_password_reset_email_html(special_greeting, special_url)

        self.assertIn(special_greeting, result)
        self.assertIn(special_url, result)

    def test_password_reset_plain_with_special_characters(self):
        """Тест звичайного тексту скидання паролю зі спеціальними символами"""
        special_greeting = "Hello <Admin> & 'User'"
        special_url = "https://example.com/reset?token=xyz&id=456"

        result = get_password_reset_email_plain(special_greeting, special_url)

        self.assertIn(special_greeting, result)
        self.assertIn(special_url, result)

    def test_empty_parameters(self):
        """Тест з порожніми параметрами"""
        empty_greeting = ""
        empty_url = ""

        html_result = get_verification_email_html(empty_greeting, empty_url)
        plain_result = get_verification_email_plain(empty_greeting, empty_url)

        self.assertIsInstance(html_result, str)
        self.assertIsInstance(plain_result, str)

        reset_html_result = get_password_reset_email_html(empty_greeting, empty_url)
        reset_plain_result = get_password_reset_email_plain(empty_greeting, empty_url)

        self.assertIsInstance(reset_html_result, str)
        self.assertIsInstance(reset_plain_result, str)

    @patch('users.utils.email_templates.gettext')
    def test_gettext_translation_integration(self, mock_gettext):
        """Тест інтеграції з системою перекладів"""
        translations = {
            'Thank you for registering with SmartStudy!': 'Дякуємо за реєстрацію в SmartStudy!',
            'Confirm email': 'Підтвердити email',
            'Reset password': 'Скинути пароль'
        }

        mock_gettext.side_effect = lambda x: translations.get(x, x)

        html_result = get_verification_email_html(self.greeting, self.activation_url)

        self.assertIn('Дякуємо за реєстрацію в SmartStudy!', html_result)
        self.assertIn('Підтвердити email', html_result)

    def test_html_structure_validity(self):
        """Тест валідності HTML структури"""
        html_verification = get_verification_email_html(self.greeting, self.activation_url)
        html_reset = get_password_reset_email_html(self.greeting, self.reset_url)

        for html in [html_verification, html_reset]:
            self.assertEqual(html.count('<html>'), html.count('</html>'))
            self.assertEqual(html.count('<body'), html.count('</body>'))
            self.assertEqual(html.count('<div'), html.count('</div>'))
            self.assertEqual(html.count('<h2'), html.count('</h2>'))

            p_open_pattern = r'<p[^>]*>'
            p_open_count = len(re.findall(p_open_pattern, html))
            p_close_count = html.count('</p>')
            self.assertEqual(p_open_count, p_close_count)

    def test_return_types(self):
        """Тест типів повернення всіх функцій"""
        functions_and_params = [
            (get_verification_email_html, self.greeting, self.activation_url),
            (get_verification_email_plain, self.greeting, self.activation_url),
            (get_password_reset_email_html, self.greeting, self.reset_url),
            (get_password_reset_email_plain, self.greeting, self.reset_url)
        ]

        for func, greeting, url in functions_and_params:
            result = func(greeting, url)
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
