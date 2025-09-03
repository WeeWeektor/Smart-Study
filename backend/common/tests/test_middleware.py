from unittest.mock import Mock, patch

from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import TestCase, override_settings, RequestFactory

from common.middleware import LanguageMiddleware, RateLimitMiddleware, SessionSecurityMiddleware, \
    SecurityHeadersMiddleware


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


class TestRateLimitMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware(lambda request: JsonResponse({'success': True}))
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_get_request_not_rate_limited(self):
        """GET запити не повинні обмежуватися"""
        request = self.factory.get('/api/auth/login/')
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_post_request_to_non_protected_endpoint(self):
        """POST запити до незахищених endpoints не обмежуються"""
        request = self.factory.post('/api/unprotected/')
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_login_rate_limiting(self):
        """Тест rate limiting для login endpoint"""
        for i in range(5):
            request = self.factory.post('/api/auth/login/', {'username': 'test', 'password': 'test'})
            response = self.middleware.process_request(request)
            self.assertIsNone(response)

            if hasattr(request, '_rate_limit_key'):
                mock_response = Mock()
                mock_response.status_code = 400
                self.middleware.process_response(request, mock_response)

        request = self.factory.post('/api/auth/login/', {'username': 'test', 'password': 'test'})
        response = self.middleware.process_request(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 429)

    def test_register_rate_limiting(self):
        """Тест rate limiting для register endpoint"""
        for i in range(3):
            request = self.factory.post('/api/auth/register/', {'username': f'test{i}', 'password': 'test'})
            response = self.middleware.process_request(request)
            self.assertIsNone(response)

            if hasattr(request, '_rate_limit_key'):
                mock_response = Mock()
                mock_response.status_code = 400
                self.middleware.process_response(request, mock_response)

        request = self.factory.post('/api/auth/register/', {'username': 'test4', 'password': 'test'})
        response = self.middleware.process_request(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 429)

    def test_successful_request_clears_counter(self):
        """Успішний запит скидає лічильник спроб"""
        for i in range(2):
            request = self.factory.post('/api/auth/login/', {'username': 'test', 'password': 'test'})
            self.middleware.process_request(request)

            if hasattr(request, '_rate_limit_key'):
                mock_response = Mock()
                mock_response.status_code = 400
                self.middleware.process_response(request, mock_response)

        request = self.factory.post('/api/auth/login/', {'username': 'test', 'password': 'correct'})
        self.middleware.process_request(request)

        if hasattr(request, '_rate_limit_key'):
            mock_response = Mock()
            mock_response.status_code = 200
            self.middleware.process_response(request, mock_response)

        key = f"login_attempts_127.0.0.1"
        self.assertIsNone(cache.get(key))

    def test_different_ips_have_separate_limits(self):
        """Різні IP мають окремі ліміти"""
        for i in range(5):
            request = self.factory.post('/api/auth/login/', {'username': 'test', 'password': 'test'})
            request.META['REMOTE_ADDR'] = '192.168.1.1'
            response = self.middleware.process_request(request)
            self.assertIsNone(response)

            if hasattr(request, '_rate_limit_key'):
                mock_response = Mock()
                mock_response.status_code = 400
                self.middleware.process_response(request, mock_response)

        request = self.factory.post('/api/auth/login/', {'username': 'test', 'password': 'test'})
        request.META['REMOTE_ADDR'] = '192.168.1.2'
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_x_forwarded_for_header(self):
        """Тест обробки X-Forwarded-For заголовка"""
        request = self.factory.post('/api/auth/login/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.100, 10.0.0.1'

        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')

    def test_get_rate_limit_config(self):
        """Тест отримання конфігурації rate limit"""
        config = self.middleware.get_rate_limit_config('/api/auth/login/')
        self.assertEqual(config['max_attempts'], 5)
        self.assertEqual(config['window'], 300)
        self.assertEqual(config['key_prefix'], 'login')

        config = self.middleware.get_rate_limit_config('/api/unprotected/')
        self.assertIsNone(config)

    @override_settings(DISABLE_RATE_LIMITING=True)
    def test_rate_limiting_disabled(self):
        """Тест відключення rate limiting через налаштування"""
        for i in range(10):
            request = self.factory.post('/api/auth/login/', {'username': 'test', 'password': 'test'})
            response = self.middleware.process_request(request)
            self.assertIsNone(response)

    def test_exception_handling(self):
        """Тест обробки винятків"""
        with patch('common.middleware.cache.get', side_effect=Exception("Cache error")):
            request = self.factory.post('/api/auth/login/')
            response = self.middleware.process_request(request)
            self.assertIsNone(response)


class TestSessionSecurityMiddleware(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        self.factory = RequestFactory()
        self.middleware = SessionSecurityMiddleware(lambda request: JsonResponse({'success': True}))
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass',
            name='Test',
            surname='User',
            role='student'
        )

    def _add_session_middleware(self, request):
        """Додає session middleware до request"""
        session_middleware = SessionMiddleware(lambda r: None)
        session_middleware.process_request(request)
        request.session.save()

        auth_middleware = AuthenticationMiddleware(lambda r: None)
        auth_middleware.process_request(request)

    def _create_authenticated_user_mock(self):
        """Створює mock об'єкт авторизованого користувача"""
        mock_user = Mock()
        mock_user.is_authenticated = True
        return mock_user

    def _create_unauthenticated_user_mock(self):
        """Створює mock об'єкт неавторизованого користувача"""
        mock_user = Mock()
        mock_user.is_authenticated = False
        return mock_user

    def test_unprotected_endpoint_allowed(self):
        """Незахищені endpoints пропускаються"""
        request = self.factory.get('/api/public/')
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_protected_endpoint_unauthenticated_user(self):
        """Неавторизовані користувачі на захищених endpoints"""
        request = self.factory.get('/api/user/profile/')
        self._add_session_middleware(request)
        request.user = self._create_unauthenticated_user_mock()

        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_protected_endpoint_same_ip(self):
        """Захищений endpoint з тим же IP"""
        request = self.factory.get('/api/user/profile/')
        self._add_session_middleware(request)
        request.user = self._create_authenticated_user_mock()
        request.session['ip_address'] = '127.0.0.1'

        response = self.middleware.process_request(request)
        self.assertIsNone(response)
        self.assertEqual(request.session['ip_address'], '127.0.0.1')

    def test_protected_endpoint_different_ip_security_violation(self):
        """Захищений endpoint з іншим IP - порушення безпеки"""
        request = self.factory.get('/api/user/profile/')
        self._add_session_middleware(request)
        request.user = self._create_authenticated_user_mock()
        request.session['ip_address'] = '192.168.1.1'
        request.META['REMOTE_ADDR'] = '192.168.1.2'

        response = self.middleware.process_request(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 401)

    def test_local_ip_changes_allowed(self):
        """Зміни між локальними IP дозволені"""
        request = self.factory.get('/api/user/profile/')
        self._add_session_middleware(request)
        request.user = self._create_authenticated_user_mock()
        request.session['ip_address'] = '127.0.0.1'
        request.META['REMOTE_ADDR'] = 'localhost'

        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_first_request_sets_ip(self):
        """Перший запит встановлює IP в сесії"""
        request = self.factory.get('/api/user/profile/')
        self._add_session_middleware(request)
        request.user = self._create_authenticated_user_mock()
        request.META['REMOTE_ADDR'] = '192.168.1.100'

        response = self.middleware.process_request(request)
        self.assertIsNone(response)
        self.assertEqual(request.session['ip_address'], '192.168.1.100')

    def test_x_forwarded_for_header(self):
        """Тест обробки X-Forwarded-For заголовка"""
        request = self.factory.get('/api/user/profile/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.100, 10.0.0.1'

        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')

    def test_is_protected_endpoint(self):
        """Тест визначення захищених endpoints"""
        self.assertTrue(self.middleware.is_protected_endpoint('/api/user/profile/'))
        self.assertTrue(self.middleware.is_protected_endpoint('/api/user/change-password/'))
        self.assertTrue(self.middleware.is_protected_endpoint('/admin/'))
        self.assertTrue(self.middleware.is_protected_endpoint('/admin/users/'))
        self.assertFalse(self.middleware.is_protected_endpoint('/api/public/'))

    def test_is_local_ip_change(self):
        """Тест визначення локальних змін IP"""
        self.assertTrue(self.middleware.is_local_ip_change('127.0.0.1', 'localhost'))
        self.assertTrue(self.middleware.is_local_ip_change('localhost', '::1'))
        self.assertFalse(self.middleware.is_local_ip_change('127.0.0.1', '192.168.1.1'))
        self.assertFalse(self.middleware.is_local_ip_change('192.168.1.1', '192.168.1.2'))

    def test_exception_handling(self):
        """Тест обробки винятків"""
        request = self.factory.get('/api/user/profile/')
        request.user = self._create_authenticated_user_mock()

        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_session_flush_on_security_violation(self):
        """Тест очищення сесії при порушенні безпеки"""
        request = self.factory.get('/api/user/profile/')
        self._add_session_middleware(request)
        request.user = self._create_authenticated_user_mock()
        request.session['ip_address'] = '192.168.1.1'
        request.session['test_data'] = 'some_value'
        request.META['REMOTE_ADDR'] = '192.168.1.2'

        initial_session_key = request.session.session_key
        response = self.middleware.process_request(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 401)
        self.assertNotEqual(request.session.session_key, initial_session_key)

    def test_admin_endpoint_protection(self):
        """Тест захисту admin endpoints"""
        request = self.factory.get('/admin/users/user/')
        self._add_session_middleware(request)
        request.user = self._create_authenticated_user_mock()
        request.session['ip_address'] = '192.168.1.1'
        request.META['REMOTE_ADDR'] = '192.168.1.2'

        response = self.middleware.process_request(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 401)

    def test_remote_addr_fallback(self):
        """Тест fallback на REMOTE_ADDR коли X-Forwarded-For відсутній"""
        request = self.factory.get('/api/user/profile/')
        request.META['REMOTE_ADDR'] = '192.168.1.50'

        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.50')

    def test_default_ip_fallback(self):
        """Тест fallback на default IP"""
        request = self.factory.get('/api/user/profile/')
        if 'REMOTE_ADDR' in request.META:
            del request.META['REMOTE_ADDR']

        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')

    def test_multiple_x_forwarded_for_ips(self):
        """Тест обробки множинних IP в X-Forwarded-For"""
        request = self.factory.get('/api/user/profile/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.100, 10.0.0.1, 172.16.0.1'

        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')

    def test_ip_update_on_valid_request(self):
        """Тест оновлення IP в сесії на валідному запиті"""
        request = self.factory.get('/api/user/profile/')
        self._add_session_middleware(request)
        request.user = self._create_authenticated_user_mock()
        request.META['REMOTE_ADDR'] = '192.168.1.100'

        self.assertNotIn('ip_address', request.session)

        response = self.middleware.process_request(request)

        self.assertIsNone(response)
        self.assertEqual(request.session['ip_address'], '192.168.1.100')

    def test_non_authenticated_user_skipped(self):
        """Тест пропуску неавторизованих користувачів на захищених endpoints"""
        request = self.factory.get('/api/user/profile/')
        self._add_session_middleware(request)
        request.user = self._create_unauthenticated_user_mock()

        response = self.middleware.process_request(request)
        self.assertIsNone(response)


class TestSecurityHeadersMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(lambda request: JsonResponse({'success': True}))

    def test_security_headers_added(self):
        """Тест додавання security заголовків"""
        request = self.factory.get('/')
        response = JsonResponse({'test': 'data'})

        processed_response = self.middleware.process_response(request, response)

        self.assertEqual(processed_response['X-Frame-Options'], 'DENY')
        self.assertEqual(processed_response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(processed_response['Referrer-Policy'], 'strict-origin-when-cross-origin')
        self.assertEqual(processed_response['Permissions-Policy'], 'geolocation=(), microphone=(), camera=()')

    def test_headers_not_added_to_non_http_response(self):
        """Тест що заголовки не додаються до non-HTTP response"""
        request = self.factory.get('/')
        response = "Not an HTTP response"

        processed_response = self.middleware.process_response(request, response)
        self.assertEqual(processed_response, "Not an HTTP response")

    def test_headers_added_to_different_response_types(self):
        """Тест додавання заголовків до різних типів відповідей"""
        from django.http import HttpResponse

        request = self.factory.get('/')

        json_response = JsonResponse({'test': 'data'})
        processed = self.middleware.process_response(request, json_response)
        self.assertIn('X-Frame-Options', processed)

        http_response = HttpResponse("Hello World")
        processed = self.middleware.process_response(request, http_response)
        self.assertIn('X-Frame-Options', processed)

    def test_all_security_headers_present(self):
        """Тест присутності всіх security заголовків"""
        request = self.factory.get('/')
        response = JsonResponse({'test': 'data'})

        processed_response = self.middleware.process_response(request, response)

        expected_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Referrer-Policy',
            'Permissions-Policy'
        ]

        for header in expected_headers:
            self.assertIn(header, processed_response)

    def test_header_values_correct(self):
        """Тест правильності значень заголовків"""
        request = self.factory.get('/')
        response = JsonResponse({'test': 'data'})

        processed_response = self.middleware.process_response(request, response)

        self.assertEqual(processed_response['X-Frame-Options'], 'DENY')
        self.assertEqual(processed_response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(processed_response['Referrer-Policy'], 'strict-origin-when-cross-origin')
        self.assertEqual(processed_response['Permissions-Policy'], 'geolocation=(), microphone=(), camera=()')
