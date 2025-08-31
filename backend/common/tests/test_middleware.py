from unittest.mock import Mock, patch
from django.test import TestCase, override_settings
from django.http import HttpRequest, HttpResponse

from common.middleware import LanguageMiddleware


class TestLanguageMiddleware(TestCase):
    def setUp(self):
        self.get_response = Mock(return_value=HttpResponse())
        self.middleware = LanguageMiddleware(self.get_response)
        self.request = HttpRequest()

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    @patch('django.utils.translation.activate')
    @patch('django.utils.translation.deactivate')
    def test_middleware_basic_flow(self, mock_deactivate, mock_activate,
                                   mock_validate, mock_get_language):
        """Тест основного потоку middleware"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        self.middleware(self.request)

        mock_get_language.assert_called_once_with(self.request)
        mock_validate.assert_called_once_with('en')
        mock_activate.assert_called_once_with('en')
        self.assertEqual(self.request.LANGUAGE_CODE, 'en')
        mock_deactivate.assert_called_once()
        self.get_response.assert_called_once_with(self.request)

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    @patch('django.utils.translation.activate')
    def test_middleware_ukrainian_language(self, mock_activate, mock_validate, mock_get_language):
        """Тест з українською мовою"""
        mock_get_language.return_value = 'uk'
        mock_validate.return_value = 'uk'

        response = self.middleware(self.request)

        mock_activate.assert_called_once_with('uk')
        self.assertEqual(self.request.LANGUAGE_CODE, 'uk')
        self.assertEqual(response['X-Current-Language'], 'uk')

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    @patch('django.utils.translation.activate')
    def test_middleware_language_validation(self, mock_activate, mock_validate, mock_get_language):
        """Тест валідації мови"""
        mock_get_language.return_value = 'invalid'
        mock_validate.return_value = 'en'  # fallback до en

        self.middleware(self.request)

        mock_get_language.assert_called_once_with(self.request)
        mock_validate.assert_called_once_with('invalid')
        mock_activate.assert_called_once_with('en')
        self.assertEqual(self.request.LANGUAGE_CODE, 'en')

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    def test_response_cookie_setting(self, mock_validate, mock_get_language):
        """Тест встановлення cookie в response"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        response = self.middleware(self.request)

        cookie = response.cookies.get('django_language')
        self.assertIsNotNone(cookie)
        self.assertEqual(cookie.value, 'en')
        self.assertEqual(cookie['max-age'], 365 * 24 * 60 * 60)
        self.assertFalse(cookie['httponly'])
        self.assertEqual(cookie['samesite'], 'Lax')
        self.assertEqual(cookie['path'], '/')

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    @override_settings(SESSION_COOKIE_SECURE=True)
    def test_cookie_secure_setting_true(self, mock_validate, mock_get_language):
        """Тест secure cookie коли SESSION_COOKIE_SECURE=True"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        response = self.middleware(self.request)

        cookie = response.cookies.get('django_language')
        self.assertEqual(cookie['secure'], True)

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    @override_settings(SESSION_COOKIE_SECURE=False)
    def test_cookie_secure_setting_false(self, mock_validate, mock_get_language):
        """Тест secure cookie коли SESSION_COOKIE_SECURE=False"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        with patch('common.middleware.settings') as mock_settings:
            mock_settings.SESSION_COOKIE_SECURE = False

            response = self.middleware(self.request)

            cookie = response.cookies.get('django_language')
            self.assertFalse(cookie['secure'])

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    def test_response_header_setting(self, mock_validate, mock_get_language):
        """Тест встановлення X-Current-Language header"""
        mock_get_language.return_value = 'uk'
        mock_validate.return_value = 'uk'

        response = self.middleware(self.request)

        self.assertEqual(response['X-Current-Language'], 'uk')

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    def test_middleware_calls_get_response(self, mock_validate, mock_get_language):
        """Тест що middleware викликає get_response з request"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        self.middleware(self.request)

        self.get_response.assert_called_once_with(self.request)

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    @patch('django.utils.translation.activate')
    @patch('django.utils.translation.deactivate')
    def test_translation_deactivate_called_after_response(self, mock_deactivate,
                                                          mock_activate, mock_validate,
                                                          mock_get_language):
        """Тест що translation.deactivate викликається після отримання response"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        self.middleware(self.request)

        mock_activate.assert_called_once_with('en')
        mock_deactivate.assert_called_once()
        self.get_response.assert_called_once_with(self.request)

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    def test_request_language_code_attribute(self, mock_validate, mock_get_language):
        """Тест що request.LANGUAGE_CODE встановлюється правильно"""
        mock_get_language.return_value = 'fr'
        mock_validate.return_value = 'fr'

        self.assertFalse(hasattr(self.request, 'LANGUAGE_CODE'))

        self.middleware(self.request)

        self.assertEqual(self.request.LANGUAGE_CODE, 'fr')

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    def test_middleware_with_different_response_types(self, mock_validate, mock_get_language):
        """Тест middleware з різними типами response"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        json_response = HttpResponse('{"test": "data"}', content_type='application/json')
        self.get_response.return_value = json_response

        response = self.middleware(self.request)

        self.assertEqual(response['X-Current-Language'], 'en')
        self.assertIsNotNone(response.cookies.get('django_language'))

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    @patch('django.utils.translation.deactivate')
    def test_middleware_exception_handling(self, mock_deactivate, mock_validate, mock_get_language):
        """Тест що deactivate викликається навіть при винятках"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'
        self.get_response.side_effect = Exception('Test exception')

        with self.assertRaises(Exception):
            self.middleware(self.request)

        mock_deactivate.assert_not_called()

    def test_middleware_initialization(self):
        """Тест ініціалізації middleware"""
        get_response_func = Mock()
        middleware = LanguageMiddleware(get_response_func)

        self.assertEqual(middleware.get_response, get_response_func)

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    def test_cookie_attributes_complete(self, mock_validate, mock_get_language):
        """Тест всіх атрибутів cookie"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        response = self.middleware(self.request)
        cookie = response.cookies.get('django_language')

        self.assertEqual(cookie.value, 'en')
        self.assertEqual(cookie['max-age'], 365 * 24 * 60 * 60)
        self.assertFalse(cookie['httponly'])
        self.assertEqual(cookie['samesite'], 'Lax')
        self.assertEqual(cookie['path'], '/')

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    @patch('django.utils.translation.activate')
    def test_multiple_language_changes(self, mock_activate,
                                       mock_validate, mock_get_language):
        """Тест послідовних змін мови"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        response1 = self.middleware(self.request)
        self.assertEqual(response1['X-Current-Language'], 'en')

        mock_get_language.return_value = 'uk'
        mock_validate.return_value = 'uk'

        request2 = HttpRequest()
        response2 = self.middleware(request2)
        self.assertEqual(response2['X-Current-Language'], 'uk')

        mock_activate.assert_any_call('en')
        mock_activate.assert_any_call('uk')

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    def test_cookie_security_attributes(self, mock_validate, mock_get_language):
        """Тест security атрибутів cookie"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        response = self.middleware(self.request)
        cookie = response.cookies.get('django_language')

        self.assertNotIn('\r', cookie.value)
        self.assertNotIn('\n', cookie.value)
        self.assertNotIn(';', cookie.value)
        self.assertNotIn('\x00', cookie.value)

    @patch('common.middleware.get_language_from_request')
    @patch('common.middleware.validate_language')
    def test_response_header_security(self, mock_validate, mock_get_language):
        """Тест безпеки response headers"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        response = self.middleware(self.request)

        lang_header = response['X-Current-Language']
        self.assertNotIn('\r', lang_header)
        self.assertNotIn('\n', lang_header)
        self.assertNotIn('\x00', lang_header)
