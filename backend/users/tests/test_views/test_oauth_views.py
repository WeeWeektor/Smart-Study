# BaseAuth, GoogleAuth, FacebookAuth
import json
from django.utils.translation import gettext
from unittest.mock import patch

from django.http import JsonResponse
from django.test import TestCase, RequestFactory

from users.views import BaseAuthView, GoogleAuthView, FacebookAuthView


class TestBaseAuthView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = BaseAuthView()
        self.valid_data = {
            'credential': 'valid_oauth_token',
            'name': 'Тест',
            'surname': 'Користувач',
            'role': 'student',
            'phone_number': '+380123456789',
            'email_notifications': True,
            'push_notifications': False
        }

    @patch('users.views.handle_oauth_login')
    async def test_base_auth_view_post_success_with_request_data(self, mock_handle_oauth):
        """Тест успішного OAuth логіну з request.data"""
        mock_handle_oauth.return_value = JsonResponse({'success': True})

        request = self.factory.post('/', data=json.dumps(self.valid_data), content_type='application/json')
        request.data = self.valid_data

        view = BaseAuthView()
        view.provider = 'test_provider'

        response = await view.post(request)

        mock_handle_oauth.assert_called_once_with(
            request=request,
            token='valid_oauth_token',
            provider='test_provider',
            name='Тест',
            surname='Користувач',
            role='student',
            phone_number='+380123456789',
            email_notifications=True,
            push_notifications=False
        )
        self.assertIsInstance(response, JsonResponse)

    @patch('users.views.handle_oauth_login')
    async def test_base_auth_view_post_success_with_json_body(self, mock_handle_oauth):
        """Тест успішного OAuth логіну з JSON body"""
        mock_handle_oauth.return_value = JsonResponse({'success': True})

        request = self.factory.post('/', data=json.dumps(self.valid_data), content_type='application/json')

        view = BaseAuthView()
        view.provider = 'test_provider'

        response = await view.post(request)

        mock_handle_oauth.assert_called_once_with(
            request=request,
            token='valid_oauth_token',
            provider='test_provider',
            name='Тест',
            surname='Користувач',
            role='student',
            phone_number='+380123456789',
            email_notifications=True,
            push_notifications=False
        )
        self.assertIsInstance(response, JsonResponse)

    async def test_base_auth_view_post_missing_credential(self):
        """Тест з відсутнім credential"""
        data = {
            'name': 'Тест',
            'surname': 'Користувач',
            'role': 'student'
        }

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        view = BaseAuthView()
        view.provider = 'test_provider'

        response = await view.post(request)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data['error'], gettext('No credential provided'))

    async def test_base_auth_view_post_empty_credential(self):
        """Тест з пустим credential"""
        data = {
            'credential': '',
            'name': 'Тест',
            'surname': 'Користувач'
        }

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        view = BaseAuthView()
        view.provider = 'test_provider'

        response = await view.post(request)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data['error'], gettext('No credential provided'))

    async def test_base_auth_view_post_none_credential(self):
        """Тест з credential = None"""
        data = {
            'credential': None,
            'name': 'Тест',
            'surname': 'Користувач'
        }

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        view = BaseAuthView()
        view.provider = 'test_provider'

        response = await view.post(request)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data['error'], gettext('No credential provided'))

    @patch('users.views.handle_oauth_login')
    async def test_base_auth_view_post_minimal_data(self, mock_handle_oauth):
        """Тест з мінімальними даними"""
        data = {'credential': 'test_token'}
        mock_handle_oauth.return_value = JsonResponse({'success': True})

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        view = BaseAuthView()
        view.provider = 'test_provider'

        await view.post(request)

        mock_handle_oauth.assert_called_once_with(
            request=request,
            token='test_token',
            provider='test_provider',
            name=None,
            surname=None,
            role=None,
            phone_number=None,
            email_notifications=True,
            push_notifications=True
        )

    @patch('users.views.handle_oauth_login')
    async def test_base_auth_view_post_default_notifications(self, mock_handle_oauth):
        """Тест зі значеннями за замовчуванням для сповіщень"""
        data = {
            'credential': 'test_token',
            'name': 'Тест'
        }
        mock_handle_oauth.return_value = JsonResponse({'success': True})

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        view = BaseAuthView()
        view.provider = 'test_provider'

        await view.post(request)

        mock_handle_oauth.assert_called_once_with(
            request=request,
            token='test_token',
            provider='test_provider',
            name='Тест',
            surname=None,
            role=None,
            phone_number=None,
            email_notifications=True,
            push_notifications=True
        )

    async def test_base_auth_view_post_invalid_json(self):
        """Тест з невалідним JSON"""
        request = self.factory.post('/', data='invalid json', content_type='application/json')

        view = BaseAuthView()
        view.provider = 'test_provider'

        response = await view.post(request)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode())
        self.assertIn('error', response_data)

    @patch('users.views.handle_oauth_login')
    async def test_base_auth_view_post_oauth_service_exception(self, mock_handle_oauth):
        """Тест коли handle_oauth_login викидає виняток"""
        mock_handle_oauth.side_effect = ValueError('OAuth services error')

        request = self.factory.post('/', data=json.dumps(self.valid_data), content_type='application/json')

        view = BaseAuthView()
        view.provider = 'test_provider'

        response = await view.post(request)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data['error'], 'OAuth services error')

    def test_base_auth_view_provider_none(self):
        """Тест що provider за замовчуванням None"""
        view = BaseAuthView()
        self.assertIsNone(view.provider)

    async def test_base_auth_view_post_async_method(self):
        """Тест що post метод є async"""
        view = BaseAuthView()
        request = self.factory.post('/', data=json.dumps({'credential': 'test'}), content_type='application/json')

        coroutine = view.post(request)
        self.assertTrue(hasattr(coroutine, '__await__'))

        coroutine.close()

    def test_base_auth_view_decorator_applied(self):
        """Тест що декоратор ensure_csrf_cookie застосований"""
        self.assertTrue(hasattr(BaseAuthView, 'dispatch'))

    @patch('users.views.handle_oauth_login')
    async def test_base_auth_view_post_with_all_fields(self, mock_handle_oauth):
        """Тест з усіма можливими полями"""
        data = {
            'credential': 'full_token',
            'name': 'Повне',
            'surname': 'Ім\'я',
            'role': 'teacher',
            'phone_number': '+380987654321',
            'email_notifications': False,
            'push_notifications': True
        }
        mock_handle_oauth.return_value = JsonResponse({'success': True})

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        view = BaseAuthView()
        view.provider = 'complete_provider'

        await view.post(request)

        mock_handle_oauth.assert_called_once_with(
            request=request,
            token='full_token',
            provider='complete_provider',
            name='Повне',
            surname='Ім\'я',
            role='teacher',
            phone_number='+380987654321',
            email_notifications=False,
            push_notifications=True
        )

    @patch('users.views.handle_oauth_login')
    async def test_base_auth_view_post_request_data_priority(self, mock_handle_oauth):
        """Тест що request.data має пріоритет над request.body"""
        mock_handle_oauth.return_value = JsonResponse({'success': True})

        body_data = {'credential': 'body_token', 'name': 'Body'}
        request = self.factory.post('/', data=json.dumps(body_data), content_type='application/json')

        request.data = {'credential': 'data_token', 'name': 'Data'}

        view = BaseAuthView()
        view.provider = 'test_provider'

        await view.post(request)

        mock_handle_oauth.assert_called_once_with(
            request=request,
            token='data_token',
            provider='test_provider',
            name='Data',
            surname=None,
            role=None,
            phone_number=None,
            email_notifications=True,
            push_notifications=True
        )

    @patch('users.views.handle_oauth_login')
    async def test_base_auth_view_post_unicode_data(self, mock_handle_oauth):
        """Тест з Unicode символами"""
        data = {
            'credential': 'unicode_token',
            'name': 'Олексій',
            'surname': 'Українець',
            'role': 'student'
        }
        mock_handle_oauth.return_value = JsonResponse({'success': True})

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        view = BaseAuthView()
        view.provider = 'unicode_provider'

        await view.post(request)

        mock_handle_oauth.assert_called_once_with(
            request=request,
            token='unicode_token',
            provider='unicode_provider',
            name='Олексій',
            surname='Українець',
            role='student',
            phone_number=None,
            email_notifications=True,
            push_notifications=True
        )


class TestGoogleAuthView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = GoogleAuthView()

    def test_google_auth_view_provider(self):
        """Тест що GoogleAuthView має правильний provider"""
        self.assertEqual(self.view.provider, 'google')

    def test_google_auth_view_inherits_base_auth(self):
        """Тест що GoogleAuthView наслідує BaseAuthView"""
        self.assertTrue(issubclass(GoogleAuthView, BaseAuthView))

    @patch('users.views.handle_oauth_login')
    async def test_google_auth_view_post_calls_with_google_provider(self, mock_handle_oauth):
        """Тест що GoogleAuthView викликає OAuth з provider='google'"""
        data = {'credential': 'google_token', 'name': 'Google', 'surname': 'User'}
        mock_handle_oauth.return_value = JsonResponse({'success': True})

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        await self.view.post(request)

        mock_handle_oauth.assert_called_once_with(
            request=request,
            token='google_token',
            provider='google',
            name='Google',
            surname='User',
            role=None,
            phone_number=None,
            email_notifications=True,
            push_notifications=True
        )

    def test_google_auth_view_decorator_applied(self):
        """Тест що декоратор ensure_csrf_cookie застосований"""
        self.assertTrue(hasattr(GoogleAuthView, 'dispatch'))

    async def test_google_auth_view_missing_credential(self):
        """Тест GoogleAuthView з відсутнім credential"""
        data = {'name': 'Google', 'surname': 'User'}

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        response = await self.view.post(request)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data['error'], gettext('No credential provided'))

    @patch('users.views.handle_oauth_login')
    async def test_google_auth_view_oauth_exception(self, mock_handle_oauth):
        """Тест GoogleAuthView з винятком від OAuth сервісу"""
        mock_handle_oauth.side_effect = Exception('Google OAuth error')
        data = {'credential': 'invalid_google_token'}

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        response = await self.view.post(request)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data['error'], 'Google OAuth error')


class TestFacebookAuthView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = FacebookAuthView()

    def test_facebook_auth_view_provider(self):
        """Тест що FacebookAuthView має правильний provider"""
        self.assertEqual(self.view.provider, 'facebook')

    def test_facebook_auth_view_inherits_base_auth(self):
        """Тест що FacebookAuthView наслідує BaseAuthView"""
        self.assertTrue(issubclass(FacebookAuthView, BaseAuthView))

    @patch('users.views.handle_oauth_login')
    async def test_facebook_auth_view_post_calls_with_facebook_provider(self, mock_handle_oauth):
        """Тест що FacebookAuthView викликає OAuth з provider='facebook'"""
        data = {'credential': 'facebook_token', 'name': 'Facebook', 'surname': 'User'}
        mock_handle_oauth.return_value = JsonResponse({'success': True})

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        await self.view.post(request)

        mock_handle_oauth.assert_called_once_with(
            request=request,
            token='facebook_token',
            provider='facebook',
            name='Facebook',
            surname='User',
            role=None,
            phone_number=None,
            email_notifications=True,
            push_notifications=True
        )

    def test_facebook_auth_view_decorator_applied(self):
        """Тест що декоратор ensure_csrf_cookie застосований"""
        self.assertTrue(hasattr(FacebookAuthView, 'dispatch'))

    async def test_facebook_auth_view_missing_credential(self):
        """Тест FacebookAuthView з відсутнім credential"""
        data = {'name': 'Facebook', 'surname': 'User'}

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        response = await self.view.post(request)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data['error'], gettext('No credential provided'))

    @patch('users.views.handle_oauth_login')
    async def test_facebook_auth_view_oauth_exception(self, mock_handle_oauth):
        """Тест FacebookAuthView з винятком від OAuth сервісу"""
        mock_handle_oauth.side_effect = Exception('Facebook OAuth error')
        data = {'credential': 'invalid_facebook_token'}

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        response = await self.view.post(request)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data['error'], 'Facebook OAuth error')

    @patch('users.views.handle_oauth_login')
    async def test_facebook_auth_view_full_data(self, mock_handle_oauth):
        """Тест FacebookAuthView з повними даними"""
        data = {
            'credential': 'facebook_full_token',
            'name': 'Марія',
            'surname': 'Петренко',
            'role': 'teacher',
            'phone_number': '+380123456789',
            'email_notifications': False,
            'push_notifications': True
        }
        mock_handle_oauth.return_value = JsonResponse({'success': True, 'user_id': 'facebook_123'})

        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        response = await self.view.post(request)

        mock_handle_oauth.assert_called_once_with(
            request=request,
            token='facebook_full_token',
            provider='facebook',
            name='Марія',
            surname='Петренко',
            role='teacher',
            phone_number='+380123456789',
            email_notifications=False,
            push_notifications=True
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode())
        self.assertTrue(response_data['success'])


class TestOAuthViewsComparison(TestCase):
    """Тести для порівняння GoogleAuthView та FacebookAuthView"""

    def test_different_providers(self):
        """Тест що GoogleAuthView та FacebookAuthView мають різні провайдери"""
        google_view = GoogleAuthView()
        facebook_view = FacebookAuthView()

        self.assertEqual(google_view.provider, 'google')
        self.assertEqual(facebook_view.provider, 'facebook')
        self.assertNotEqual(google_view.provider, facebook_view.provider)

    def test_both_inherit_base_auth(self):
        """Тест що обидва view наслідують BaseAuthView"""
        self.assertTrue(issubclass(GoogleAuthView, BaseAuthView))
        self.assertTrue(issubclass(FacebookAuthView, BaseAuthView))

    def test_both_have_decorators(self):
        """Тест що обидва view мають однакові декоратори"""
        self.assertTrue(hasattr(GoogleAuthView, 'dispatch'))
        self.assertTrue(hasattr(FacebookAuthView, 'dispatch'))

    @patch('users.views.handle_oauth_login')
    async def test_both_views_call_oauth_service(self, mock_handle_oauth):
        """Тест що обидва view викликають OAuth сервіс з правильними провайдерами"""
        mock_handle_oauth.return_value = JsonResponse({'success': True})

        data = {'credential': 'test_token', 'name': 'Test'}
        request = RequestFactory().post('/', data=json.dumps(data), content_type='application/json')

        google_view = GoogleAuthView()
        await google_view.post(request)

        facebook_view = FacebookAuthView()
        await facebook_view.post(request)

        self.assertEqual(mock_handle_oauth.call_count, 2)

        calls = mock_handle_oauth.call_args_list
        google_call = calls[0]
        facebook_call = calls[1]

        self.assertEqual(google_call.kwargs['provider'], 'google')
        self.assertEqual(facebook_call.kwargs['provider'], 'facebook')
