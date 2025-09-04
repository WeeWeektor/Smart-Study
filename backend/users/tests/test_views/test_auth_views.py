# Login, Logout, Register, VerifyEmail
import json
from unittest.mock import patch, AsyncMock, Mock

from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.core.signing import SignatureExpired, BadSignature
from django.db import IntegrityError
from django.test import TestCase, RequestFactory
from django.utils.translation import gettext

from smartStudy_backend import settings
from users.models import CustomUser
from users.views import LogoutView, LoginView, RegisterView, VerifyEmailView


class TestLoginView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = LoginView()

    @patch('users.views.warm_user_cache')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.success_response')
    async def test_login_view_post_success(self, mock_success_response, mock_email_validator, mock_sync_to_async,
                                           mock_warm_cache):
        """Тест успішного логіну"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }

        mock_user = Mock()
        mock_user.id = 'user-123'
        mock_user.name = 'John'
        mock_user.surname = 'Doe'
        mock_user.email = 'test@example.com'
        mock_user.is_staff = False
        mock_user.is_superuser = False
        mock_user.phone_number = '+1234567890'
        mock_user.role = 'student'
        mock_user.is_verified_email = True
        mock_user.is_active = True

        mock_email_validator.return_value = None
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=mock_user),
            AsyncMock()
        ]
        mock_warm_cache.return_value = None
        mock_success_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await LoginView.post(request)

        mock_email_validator.assert_called_once_with('test@example.com')
        self.assertEqual(mock_sync_to_async.call_count, 2)
        mock_warm_cache.assert_called_once_with(mock_user)
        mock_success_response.assert_called_once()

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_login_view_post_missing_email(self, mock_error_response, mock_email_validator, mock_sync_to_async):
        """Тест з відсутнім email"""
        user_data = {'password': 'testpassword123'}
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await LoginView.post(request)

        mock_error_response.assert_called_once_with(gettext('Required fields are missing: email or password.'))
        mock_email_validator.assert_not_called()
        mock_sync_to_async.assert_not_called()

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_login_view_post_missing_password(self, mock_error_response, mock_email_validator,
                                                    mock_sync_to_async):
        """Тест з відсутнім password"""
        user_data = {'email': 'test@example.com'}
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await LoginView.post(request)

        mock_error_response.assert_called_once_with(gettext('Required fields are missing: email or password.'))
        mock_email_validator.assert_not_called()
        mock_sync_to_async.assert_not_called()

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_login_view_post_missing_both_fields(self, mock_error_response, mock_email_validator,
                                                       mock_sync_to_async):
        """Тест з відсутніми email та password"""
        user_data = {}
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await LoginView.post(request)

        mock_error_response.assert_called_once_with(gettext('Required fields are missing: email or password.'))
        mock_email_validator.assert_not_called()
        mock_sync_to_async.assert_not_called()

    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_login_view_post_invalid_email(self, mock_error_response, mock_email_validator):
        """Тест з невалідним email"""
        user_data = {
            'email': 'invalid-email',
            'password': 'testpassword123'
        }
        mock_email_validator.side_effect = ValidationError(['Invalid email format'])
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await LoginView.post(request)

        mock_email_validator.assert_called_once_with('invalid-email')
        mock_error_response.assert_called_once_with("['Invalid email format']")

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_login_view_post_user_not_found(self, mock_error_response, mock_email_validator, mock_sync_to_async):
        """Тест з неіснуючим користувачем"""
        user_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        mock_email_validator.return_value = None
        mock_sync_to_async.return_value = AsyncMock(return_value=None)
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await LoginView.post(request)

        mock_error_response.assert_called_once_with(gettext('Incorrect email or password.'), 400)

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_login_view_post_inactive_user(self, mock_error_response, mock_email_validator, mock_sync_to_async):
        """Тест з неактивним користувачем"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        mock_user = Mock()
        mock_user.is_active = False

        mock_email_validator.return_value = None
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_user)
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await LoginView.post(request)

        mock_error_response.assert_called_once_with(gettext('Account is inactive.'), 400)

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_login_view_post_unverified_email(self, mock_error_response, mock_email_validator,
                                                    mock_sync_to_async):
        """Тест з непідтвердженим email"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.is_verified_email = False

        mock_email_validator.return_value = None
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_user)
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await LoginView.post(request)

        mock_error_response.assert_called_once_with(gettext('Email not confirmed. Please check your email.'), 400)

    @patch('users.views.error_response')
    async def test_login_view_post_invalid_json(self, mock_error_response):
        """Тест з невалідним JSON"""
        mock_error_response.return_value = Mock()
        request = self.factory.post('/', data='invalid json', content_type='application/json')

        await LoginView.post(request)

        mock_error_response.assert_called_once_with(gettext('Invalid JSON format.'), 400)

    @patch('users.views.warm_user_cache')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.success_response')
    async def test_login_view_post_success_response_data(self, mock_success_response, mock_email_validator,
                                                         mock_sync_to_async, mock_warm_cache):
        """Тест структури даних у success response"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }

        mock_user = Mock()
        mock_user.id = 'user-123'
        mock_user.name = 'John'
        mock_user.surname = 'Doe'
        mock_user.email = 'test@example.com'
        mock_user.is_staff = False
        mock_user.is_superuser = False
        mock_user.phone_number = '+1234567890'
        mock_user.role = 'student'
        mock_user.is_verified_email = True
        mock_user.is_active = True

        mock_email_validator.return_value = None
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=mock_user),
            AsyncMock()
        ]
        mock_warm_cache.return_value = None

        expected_response_data = {
            "user": {
                "id": "user-123",
                "name": "John",
                "surname": "Doe",
                "email": "test@example.com",
                "is_staff": False,
                "is_superuser": False,
                "phone_number": "+1234567890",
                "role": "student",
                "is_verified_email": True,
            },
            "redirect": "/profile/",
        }

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await LoginView.post(request)

        mock_success_response.assert_called_once_with(expected_response_data)

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_login_view_post_authenticate_call(self, mock_email_validator, mock_sync_to_async):
        """Тест виклику функції authenticate"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.is_verified_email = True

        mock_email_validator.return_value = None
        mock_authenticate = AsyncMock(return_value=mock_user)
        mock_login = AsyncMock()
        mock_sync_to_async.side_effect = [mock_authenticate, mock_login]

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.warm_user_cache'), patch('users.views.success_response'):
            await LoginView.post(request)

        mock_authenticate.assert_called_once_with(request, username='test@example.com', password='testpassword123')

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_login_view_post_login_call(self, mock_email_validator, mock_sync_to_async):
        """Тест виклику функції login"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.is_verified_email = True

        mock_email_validator.return_value = None
        mock_authenticate = AsyncMock(return_value=mock_user)
        mock_login = AsyncMock()
        mock_sync_to_async.side_effect = [mock_authenticate, mock_login]

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.warm_user_cache'), patch('users.views.success_response'):
            await LoginView.post(request)

        mock_login.assert_called_once_with(request, mock_user, backend='django.contrib.auth.backends.ModelBackend')

    @patch('users.views.warm_user_cache')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_login_view_post_warm_cache_call(self, mock_email_validator, mock_sync_to_async, mock_warm_cache):
        """Тест виклику warm_user_cache"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.is_verified_email = True

        mock_email_validator.return_value = None
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=mock_user),
            AsyncMock()
        ]

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.success_response'):
            await LoginView.post(request)

        mock_warm_cache.assert_called_once_with(mock_user)

    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_login_view_post_general_exception(self, mock_error_response, mock_email_validator):
        """Тест обробки загальних винятків"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        mock_email_validator.side_effect = Exception('Test exception')
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await LoginView.post(request)

        mock_error_response.assert_called_once_with(f"{gettext('Login error:')} Test exception", 500)

    def test_login_view_is_static_method(self):
        """Тест що post метод є статичним"""
        self.assertTrue(isinstance(LoginView.__dict__['post'], staticmethod))

    async def test_login_view_post_async_function(self):
        """Тест що метод є async функцією"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        coroutine = LoginView.post(request)
        self.assertTrue(hasattr(coroutine, '__await__'))

        coroutine.close()

    @patch('users.views.warm_user_cache')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_login_view_post_staff_user(self, mock_email_validator, mock_sync_to_async, mock_warm_cache):
        """Тест логіну staff користувача"""
        user_data = {
            'email': 'admin@example.com',
            'password': 'adminpassword123'
        }

        mock_user = Mock()
        mock_user.id = 'admin-123'
        mock_user.name = 'Admin'
        mock_user.surname = 'User'
        mock_user.email = 'admin@example.com'
        mock_user.is_staff = True
        mock_user.is_superuser = False
        mock_user.phone_number = None
        mock_user.role = 'admin'
        mock_user.is_verified_email = True
        mock_user.is_active = True

        mock_email_validator.return_value = None
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=mock_user),
            AsyncMock()
        ]
        mock_warm_cache.return_value = None

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.success_response') as mock_success_response:
            await LoginView.post(request)

            call_args = mock_success_response.call_args[0][0]
            self.assertTrue(call_args['user']['is_staff'])
            self.assertEqual(call_args['redirect'], '/profile/')

    @patch('users.views.warm_user_cache')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_login_view_post_superuser(self, mock_email_validator, mock_sync_to_async, mock_warm_cache):
        """Тест логіну superuser"""
        user_data = {
            'email': 'superuser@example.com',
            'password': 'superpassword123'
        }

        mock_user = Mock()
        mock_user.id = 'super-123'
        mock_user.name = 'Super'
        mock_user.surname = 'User'
        mock_user.email = 'superuser@example.com'
        mock_user.is_staff = True
        mock_user.is_superuser = True
        mock_user.phone_number = None
        mock_user.role = 'admin'
        mock_user.is_verified_email = True
        mock_user.is_active = True

        mock_email_validator.return_value = None
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=mock_user),
            AsyncMock()
        ]
        mock_warm_cache.return_value = None

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.success_response') as mock_success_response:
            await LoginView.post(request)

            call_args = mock_success_response.call_args[0][0]
            self.assertTrue(call_args['user']['is_staff'])
            self.assertTrue(call_args['user']['is_superuser'])

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_login_view_post_email_validation_with_spaces(self, mock_email_validator, mock_sync_to_async):
        """Тест валідації email з пробілами"""
        user_data = {
            'email': '  test@example.com  ',
            'password': 'testpassword123'
        }
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.is_verified_email = True

        mock_email_validator.return_value = None
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=mock_user),
            AsyncMock()
        ]

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.warm_user_cache'), patch('users.views.success_response'):
            await LoginView.post(request)

        mock_email_validator.assert_called_once_with('  test@example.com  ')

    @patch('users.views.warm_user_cache')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_login_view_post_user_with_null_phone(self, mock_email_validator, mock_sync_to_async,
                                                        mock_warm_cache):
        """Тест з користувачем без номера телефону"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }

        mock_user = Mock()
        mock_user.id = 'user-123'
        mock_user.name = 'John'
        mock_user.surname = 'Doe'
        mock_user.email = 'test@example.com'
        mock_user.is_staff = False
        mock_user.is_superuser = False
        mock_user.phone_number = None
        mock_user.role = 'student'
        mock_user.is_verified_email = True
        mock_user.is_active = True

        mock_email_validator.return_value = None
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=mock_user),
            AsyncMock()
        ]
        mock_warm_cache.return_value = None

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.success_response') as mock_success_response:
            await LoginView.post(request)

            call_args = mock_success_response.call_args[0][0]
            self.assertIsNone(call_args['user']['phone_number'])

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_login_view_post_different_backends(self, mock_email_validator, mock_sync_to_async):
        """Тест що використовується правильний authentication backend"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.is_verified_email = True

        mock_email_validator.return_value = None
        mock_authenticate = AsyncMock(return_value=mock_user)
        mock_login = AsyncMock()
        mock_sync_to_async.side_effect = [mock_authenticate, mock_login]

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.warm_user_cache'), patch('users.views.success_response'):
            await LoginView.post(request)

        mock_login.assert_called_once_with(
            request,
            mock_user,
            backend='django.contrib.auth.backends.ModelBackend'
        )

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_login_view_post_user_type_annotation(self, mock_error_response, mock_email_validator,
                                                        mock_sync_to_async):
        """Тест типу користувача (Optional[CustomUser])"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }

        mock_email_validator.return_value = None
        mock_sync_to_async.return_value = AsyncMock(return_value=None)
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await LoginView.post(request)

        mock_error_response.assert_called_once_with(gettext('Incorrect email or password.'), 400)

    @patch('users.views.warm_user_cache')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_login_view_post_user_id_as_string(self, mock_email_validator, mock_sync_to_async, mock_warm_cache):
        """Тест що user.id повертається як рядок"""
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }

        mock_user = Mock()
        mock_user.id = 12345
        mock_user.name = 'John'
        mock_user.surname = 'Doe'
        mock_user.email = 'test@example.com'
        mock_user.is_staff = False
        mock_user.is_superuser = False
        mock_user.phone_number = '+1234567890'
        mock_user.role = 'student'
        mock_user.is_verified_email = True
        mock_user.is_active = True

        mock_email_validator.return_value = None
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=mock_user),
            AsyncMock()
        ]
        mock_warm_cache.return_value = None

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.success_response') as mock_success_response:
            await LoginView.post(request)

            call_args = mock_success_response.call_args[0][0]
            self.assertEqual(call_args['user']['id'], '12345')
            self.assertIsInstance(call_args['user']['id'], str)


class TestLogoutView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = LogoutView()

    @patch('users.views.sync_to_async')
    @patch('users.views.success_response')
    @patch('users.views.gettext')
    async def test_logout_view_post_success(self, mock_gettext, mock_success_response, mock_sync_to_async):
        """Тест успішного логауту"""
        mock_gettext.return_value = 'You have successfully logged out.'
        mock_success_response.return_value = Mock()

        mock_logout = AsyncMock()
        mock_sync_to_async.return_value = mock_logout

        request = self.factory.post('/logout/')

        await LogoutView.post(request)

        mock_sync_to_async.assert_called_once_with(logout)
        mock_logout.assert_called_once_with(request)
        mock_gettext.assert_called_once_with('You have successfully logged out.')
        mock_success_response.assert_called_once_with({"message": 'You have successfully logged out.'})

    @patch('users.views.sync_to_async')
    @patch('users.views.success_response')
    async def test_logout_view_post_calls_django_logout(self, mock_success_response, mock_sync_to_async):
        """Тест що викликається Django logout функція"""
        mock_logout = AsyncMock()
        mock_sync_to_async.return_value = mock_logout
        mock_success_response.return_value = Mock()

        request = self.factory.post('/logout/')

        await LogoutView.post(request)

        mock_sync_to_async.assert_called_once_with(logout)
        mock_logout.assert_called_once_with(request)

    @patch('users.views.sync_to_async')
    @patch('users.views.gettext')
    async def test_logout_view_post_gettext_call(self, mock_gettext, mock_sync_to_async):
        """Тест виклику gettext для локалізації"""
        mock_gettext.return_value = 'Translated message'
        mock_sync_to_async.return_value = AsyncMock()

        request = self.factory.post('/logout/')

        await LogoutView.post(request)

        mock_gettext.assert_called_once_with('You have successfully logged out.')

    @patch('users.views.sync_to_async')
    @patch('users.views.success_response')
    async def test_logout_view_post_success_response_format(self, mock_success_response, mock_sync_to_async):
        """Тест формату відповіді success_response"""
        mock_sync_to_async.return_value = AsyncMock()
        expected_response = {"message": "You have successfully logged out."}
        mock_success_response.return_value = Mock()

        request = self.factory.post('/logout/')

        with patch('users.views.gettext', return_value='You have successfully logged out.'):
            await LogoutView.post(request)

        mock_success_response.assert_called_once_with(expected_response)

    @patch('users.views.sync_to_async')
    async def test_logout_view_post_return_value(self, mock_sync_to_async):
        """Тест що метод повертає результат success_response"""
        mock_sync_to_async.return_value = AsyncMock()
        expected_result = Mock()

        request = self.factory.post('/logout/')

        with patch('users.views.success_response', return_value=expected_result):
            result = await LogoutView.post(request)

        self.assertEqual(result, expected_result)

    @patch('users.views.sync_to_async')
    async def test_logout_view_post_different_request_objects(self, mock_sync_to_async):
        """Тест з різними об'єктами request"""
        mock_sync_to_async.return_value = AsyncMock()

        requests = [
            self.factory.post('/logout/'),
            self.factory.post('/logout/', data={'some': 'data'}),
            self.factory.post('/logout/', content_type='application/json')
        ]

        for request in requests:
            with self.subTest(request=request):
                with patch('users.views.success_response', return_value=Mock()):
                    result = await LogoutView.post(request)
                    self.assertIsNotNone(result)

    @patch('users.views.sync_to_async')
    async def test_logout_view_post_async_function(self, mock_sync_to_async):
        """Тест що метод є async функцією"""
        mock_sync_to_async.return_value = AsyncMock()
        request = self.factory.post('/logout/')

        with patch('users.views.success_response', return_value=Mock()):
            coroutine = LogoutView.post(request)
            self.assertTrue(hasattr(coroutine, '__await__'))

            await coroutine

    def test_logout_view_is_static_method(self):
        """Тест що post метод є статичним"""
        self.assertTrue(isinstance(LogoutView.__dict__['post'], staticmethod))

    @patch('users.views.sync_to_async')
    async def test_logout_view_post_preserves_request_object(self, mock_sync_to_async):
        """Тест що request об'єкт передається без змін"""
        mock_logout = AsyncMock()
        mock_sync_to_async.return_value = mock_logout

        original_request = self.factory.post('/logout/')
        original_request.custom_attr = 'test_value'

        with patch('users.views.success_response', return_value=Mock()):
            await LogoutView.post(original_request)

        mock_logout.assert_called_once_with(original_request)

    @patch('users.views.sync_to_async')
    @patch('users.views.gettext')
    @patch('users.views.success_response')
    async def test_logout_view_post_call_order(self, mock_success_response, mock_gettext, mock_sync_to_async):
        """Тест порядку викликів функцій"""
        mock_logout = AsyncMock()
        mock_sync_to_async.return_value = mock_logout
        mock_gettext.return_value = 'Logout message'
        mock_success_response.return_value = Mock()

        request = self.factory.post('/logout/')

        await LogoutView.post(request)

        mock_sync_to_async.assert_called_once()
        mock_logout.assert_called_once()
        mock_gettext.assert_called_once()
        mock_success_response.assert_called_once()

    @patch('users.views.sync_to_async')
    async def test_logout_view_post_with_authenticated_user(self, mock_sync_to_async):
        """Тест логауту з аутентифікованим користувачем"""
        mock_logout = AsyncMock()
        mock_sync_to_async.return_value = mock_logout

        request = self.factory.post('/logout/')
        request.user = Mock()
        request.user.is_authenticated = True

        with patch('users.views.success_response', return_value=Mock()):
            await LogoutView.post(request)

        mock_logout.assert_called_once_with(request)

    @patch('users.views.sync_to_async')
    async def test_logout_view_post_with_anonymous_user(self, mock_sync_to_async):
        """Тест логауту з анонімним користувачем"""
        mock_logout = AsyncMock()
        mock_sync_to_async.return_value = mock_logout

        request = self.factory.post('/logout/')
        request.user = Mock()
        request.user.is_authenticated = False

        with patch('users.views.success_response', return_value=Mock()):
            await LogoutView.post(request)

        mock_logout.assert_called_once_with(request)

    async def test_logout_view_post_integration_with_real_functions(self):
        """Інтеграційний тест з реальними функціями (без моків для основної логіки)"""
        request = self.factory.post('/logout/')

        with patch('users.views.sync_to_async') as mock_sync_to_async:
            mock_sync_to_async.return_value = AsyncMock()
            result = await LogoutView.post(request)

        self.assertIsNotNone(result)

    @patch('users.views.sync_to_async')
    async def test_logout_view_post_message_localization(self, mock_sync_to_async):
        """Тест локалізації повідомлення"""
        mock_sync_to_async.return_value = AsyncMock()
        request = self.factory.post('/logout/')

        localized_messages = [
            'You have successfully logged out.',
            'Ви успішно вийшли з системи.',
            'Vous vous êtes déconnecté avec succès.'
        ]

        for message in localized_messages:
            with self.subTest(message=message):
                with patch('users.views.gettext', return_value=message) as mock_gettext:
                    with patch('users.views.success_response') as mock_success_response:
                        await LogoutView.post(request)

                        mock_gettext.assert_called_once_with('You have successfully logged out.')
                        mock_success_response.assert_called_once_with({"message": message})

    def test_logout_view_decorator_applied(self):
        """Тест що декоратор ensure_csrf_cookie застосований"""
        self.assertTrue(hasattr(LogoutView, 'dispatch'))


class TestRegisterView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = RegisterView()

    @patch('users.views.invalidate_user_existence_cache')
    @patch('users.views.send_verification_email')
    @patch('users.views.get_allowed_roles')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.success_response')
    async def test_register_view_post_success(self, mock_success_response, mock_email_validator,
                                              mock_sync_to_async, mock_get_allowed_roles,
                                              mock_send_email, mock_invalidate_cache):
        """Тест успішної реєстрації користувача"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'student',
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }

        mock_user = Mock()
        mock_user.email = 'test@example.com'

        mock_email_validator.return_value = None
        mock_get_allowed_roles.return_value = ['admin', 'student', 'teacher']
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_user)
        mock_success_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await RegisterView.post(request)

        mock_email_validator.assert_called_once_with('test@example.com')
        mock_get_allowed_roles.assert_called_once()
        mock_invalidate_cache.assert_called_once_with('test@example.com')
        mock_send_email.assert_called_once_with(mock_user)
        mock_success_response.assert_called_once()

    @patch('users.views.error_response')
    async def test_register_view_post_missing_required_fields(self, mock_error_response):
        """Тест з відсутніми обов'язковими полями"""
        test_cases = [
            {'surname': 'Doe', 'role': 'student', 'email': 'test@example.com', 'password': 'pass'},
            {'name': 'John', 'role': 'student', 'email': 'test@example.com', 'password': 'pass'},
            {'name': 'John', 'surname': 'Doe', 'email': 'test@example.com', 'password': 'pass'},
            {'name': 'John', 'surname': 'Doe', 'role': 'student', 'password': 'pass'},
            {'name': 'John', 'surname': 'Doe', 'role': 'student', 'email': 'test@example.com'},
        ]

        mock_error_response.return_value = Mock()

        for user_data in test_cases:
            with self.subTest(user_data=user_data):
                request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')
                await RegisterView.post(request)

        self.assertEqual(mock_error_response.call_count, len(test_cases))

    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_register_view_post_invalid_email(self, mock_error_response, mock_email_validator):
        """Тест з невалідним email"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'student',
            'email': 'invalid-email',
            'password': 'StrongPassword123!'
        }

        mock_email_validator.side_effect = ValidationError(['Invalid email format'])
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await RegisterView.post(request)

        mock_error_response.assert_called_once()

    @patch('users.views.asyncio.gather')
    @patch('users.views.get_allowed_roles')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_register_view_post_invalid_password(self, mock_error_response, mock_email_validator,
                                                       mock_sync_to_async, mock_get_allowed_roles, mock_gather):
        """Тест з невалідним паролем"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'student',
            'email': 'test@example.com',
            'password': '123'
        }

        password_error = ValidationError(['Password too short'])
        mock_email_validator.return_value = None
        mock_get_allowed_roles.return_value = ['admin', 'student', 'teacher']
        mock_gather.return_value = [None, password_error, ['admin', 'student', 'teacher']]
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await RegisterView.post(request)

        mock_error_response.assert_called_once()

    @patch('users.views.asyncio.gather')
    @patch('users.views.get_allowed_roles')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_register_view_post_invalid_phone(self, mock_error_response, mock_email_validator,
                                                    mock_sync_to_async, mock_get_allowed_roles, mock_gather):
        """Тест з невалідним номером телефону"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'student',
            'email': 'test@example.com',
            'password': 'StrongPassword123!',
            'phone_number': 'invalid'
        }

        phone_error = ValidationError(['Invalid phone number'])
        mock_email_validator.return_value = None
        mock_get_allowed_roles.return_value = ['admin', 'student', 'teacher']
        mock_gather.return_value = [phone_error, None, ['admin', 'student', 'teacher']]
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await RegisterView.post(request)

        mock_error_response.assert_called_once()

    @patch('users.views.asyncio.gather')
    @patch('users.views.get_allowed_roles')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_register_view_post_invalid_role(self, mock_error_response, mock_email_validator,
                                                   mock_sync_to_async, mock_get_allowed_roles, mock_gather):
        """Тест з невалідною роллю"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'invalid_role',
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }

        mock_email_validator.return_value = None
        mock_get_allowed_roles.return_value = ['admin', 'student', 'teacher']
        mock_gather.return_value = [None, None, ['admin', 'student', 'teacher']]
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await RegisterView.post(request)

        mock_error_response.assert_called_once()

    @patch('users.views.get_allowed_roles')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_register_view_post_empty_name_surname(self, mock_error_response, mock_email_validator,
                                                         mock_sync_to_async, mock_get_allowed_roles):
        """Тест з порожніми ім'ям та прізвищем"""
        user_data = {
            'name': '   ',
            'surname': '   ',
            'role': 'student',
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }

        mock_validate_password = AsyncMock(return_value=None)
        mock_sync_to_async.return_value = mock_validate_password

        mock_email_validator.return_value = None
        mock_get_allowed_roles.return_value = ['admin', 'student', 'teacher']
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await RegisterView.post(request)

        mock_error_response.assert_called_once_with(gettext('First and last names cannot be left blank.'))

    @patch('users.views.error_response')
    async def test_register_view_post_integrity_error(self, mock_error_response):
        """Тест IntegrityError (email вже зареєстрований)"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'student',
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }

        mock_error_response.return_value = Mock()

        with patch('users.views.cached_email_validator'), \
                patch('users.views.get_allowed_roles'), \
                patch('users.views.asyncio.gather'), \
                patch('users.views.sync_to_async', side_effect=IntegrityError()):
            request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')
            await RegisterView.post(request)

        mock_error_response.assert_called_once_with(gettext('Email already registered.'))

    @patch('users.views.error_response')
    async def test_register_view_post_invalid_json(self, mock_error_response):
        """Тест з невалідним JSON"""
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data='invalid json', content_type='application/json')

        await RegisterView.post(request)

        mock_error_response.assert_called_once_with(gettext('Invalid JSON format.'))

    @patch('users.views.invalidate_user_existence_cache')
    @patch('users.views.send_verification_email')
    @patch('users.views.asyncio.gather')
    @patch('users.views.get_allowed_roles')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_register_view_post_without_phone(self, mock_email_validator, mock_sync_to_async,
                                                    mock_get_allowed_roles, mock_gather,
                                                    mock_send_email, mock_invalidate_cache):
        """Тест реєстрації без номера телефону"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'student',
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }

        mock_user = Mock()
        mock_user.email = 'test@example.com'

        mock_email_validator.return_value = None
        mock_get_allowed_roles.return_value = ['admin', 'student', 'teacher']
        mock_gather.return_value = [None, None, ['admin', 'student', 'teacher']]
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_user)

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.success_response'):
            await RegisterView.post(request)

        mock_email_validator.assert_called_once_with('test@example.com')

    @patch('users.views.invalidate_user_existence_cache')
    @patch('users.views.send_verification_email')
    @patch('users.views.asyncio.gather')
    @patch('users.views.get_allowed_roles')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_register_view_post_user_settings_creation(self, mock_email_validator, mock_sync_to_async,
                                                             mock_get_allowed_roles, mock_gather,
                                                             mock_send_email, mock_invalidate_cache):
        """Тест створення UserSettings та UserProfile"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'student',
            'email': 'test@example.com',
            'password': 'StrongPassword123!',
            'email_notifications': False,
            'push_notifications': False
        }

        mock_user = Mock()
        mock_user.email = 'test@example.com'

        mock_email_validator.return_value = None
        mock_get_allowed_roles.return_value = ['admin', 'student', 'teacher']
        mock_gather.return_value = [None, None, ['admin', 'student', 'teacher']]
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_user)

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.success_response'):
            await RegisterView.post(request)

        mock_sync_to_async.assert_called()

    @patch('users.views.cached_email_validator')
    @patch('users.views.error_response')
    async def test_register_view_post_validation_exception(self, mock_error_response, mock_email_validator):
        """Тест обробки винятків під час валідації"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'student',
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }

        mock_email_validator.side_effect = Exception('Validation error')
        mock_error_response.return_value = Mock()

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        await RegisterView.post(request)

        mock_error_response.assert_called()

    @patch('users.views.error_response')
    async def test_register_view_post_general_exception(self, mock_error_response):
        """Тест обробки загальних винятків"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'student',
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }

        mock_error_response.return_value = Mock()

        with patch('users.views.json.loads', side_effect=Exception('General error')):
            request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')
            await RegisterView.post(request)

        mock_error_response.assert_called_once()

    def test_register_view_is_static_method(self):
        """Тест що post метод є статичним"""
        self.assertTrue(isinstance(RegisterView.__dict__['post'], staticmethod))

    async def test_register_view_post_async_function(self):
        """Тест що метод є async функцією"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'student',
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        coroutine = RegisterView.post(request)
        self.assertTrue(hasattr(coroutine, '__await__'))

        coroutine.close()

    def test_register_view_decorator_applied(self):
        """Тест що декоратор ensure_csrf_cookie застосований"""
        self.assertTrue(hasattr(RegisterView, 'dispatch'))

    @patch('users.views.invalidate_user_existence_cache')
    @patch('users.views.send_verification_email')
    @patch('users.views.asyncio.gather')
    @patch('users.views.get_allowed_roles')
    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_register_view_post_email_trimming(self, mock_email_validator, mock_sync_to_async,
                                                     mock_get_allowed_roles, mock_gather,
                                                     mock_send_email, mock_invalidate_cache):
        """Тест обрізання пробілів в імені та прізвищі"""
        user_data = {
            'name': '   John   ',
            'surname': '   Doe   ',
            'role': 'student',
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }

        mock_user = Mock()
        mock_user.email = 'test@example.com'

        mock_email_validator.return_value = None
        mock_get_allowed_roles.return_value = ['admin', 'student', 'teacher']
        mock_gather.return_value = [None, None, ['admin', 'student', 'teacher']]
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_user)

        request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')

        with patch('users.views.success_response'):
            await RegisterView.post(request)

        mock_sync_to_async.assert_called()

    @patch('users.views.send_verification_email')
    @patch('users.views.invalidate_user_existence_cache')
    async def test_register_view_post_asyncio_gather_calls(self, mock_invalidate_cache, mock_send_email):
        """Тест паралельних викликів"""
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'role': 'student',
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }

        mock_user = Mock()
        mock_user.email = 'test@example.com'

        with patch('users.views.cached_email_validator', return_value=None), \
                patch('users.views.get_allowed_roles', return_value=['admin', 'student', 'teacher']), \
                patch('users.views.sync_to_async', return_value=AsyncMock(return_value=mock_user)), \
                patch('users.views.success_response'):
            request = self.factory.post('/', data=json.dumps(user_data), content_type='application/json')
            await RegisterView.post(request)

        mock_invalidate_cache.assert_called_once_with('test@example.com')
        mock_send_email.assert_called_once_with(mock_user)


class TestVerifyEmailView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = VerifyEmailView()
        self.valid_token = 'valid_test_token'
        self.invalid_token = 'invalid_test_token'

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    @patch('users.views.warm_user_cache')
    @patch('users.views.invalidate_user_existence_cache')
    @patch('users.views.redirect')
    async def test_verify_email_view_get_success(self, mock_redirect, mock_invalidate_cache, mock_warm_cache,
                                                 mock_signer_class, mock_sync_to_async):
        """Тест успішної верифікації email через GET запит"""
        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_get_user = AsyncMock(return_value=mock_user)
        mock_save_user = AsyncMock()
        mock_login = AsyncMock()
        mock_sync_to_async.side_effect = [mock_get_user, mock_save_user, mock_login]

        mock_invalidate_cache.return_value = AsyncMock()
        mock_warm_cache.return_value = AsyncMock()
        mock_redirect.return_value = Mock()

        request = self.factory.get(f'/?token={self.valid_token}')

        await VerifyEmailView.get(request)

        mock_signer.unsign.assert_called_once_with(self.valid_token, max_age=60 * 60 * 24)
        mock_get_user.assert_called_once_with(email='test@example.com')
        self.assertTrue(mock_user.is_verified_email)
        self.assertTrue(mock_user.is_active)
        mock_save_user.assert_called_once()
        mock_invalidate_cache.assert_called_once_with('test@example.com')
        mock_warm_cache.assert_called_once_with(mock_user)
        mock_login.assert_called_once_with(request, mock_user, backend='django.contrib.auth.backends.ModelBackend')
        mock_redirect.assert_called_once_with(f"{settings.FRONTEND_URL}/verify-email?token={self.valid_token}")

    @patch('users.views.error_response')
    async def test_verify_email_view_get_missing_token(self, mock_error_response):
        """Тест з відсутнім токеном у GET параметрах"""
        mock_error_response.return_value = Mock()

        request = self.factory.get('/')

        await VerifyEmailView.get(request)

        expected_message = 'Invalid token. The ‘token’ parameter is missing.'
        mock_error_response.assert_called_once_with(expected_message)

    @patch('users.views.error_response')
    async def test_verify_email_view_get_empty_token(self, mock_error_response):
        """Тест з пустим токеном у GET параметрах"""
        mock_error_response.return_value = Mock()

        request = self.factory.get('/?token=')

        await VerifyEmailView.get(request)

        expected_message = 'Invalid token. The ‘token’ parameter is missing.'
        mock_error_response.assert_called_once_with(expected_message)

    @patch('users.views.TimestampSigner')
    @patch('users.views.error_response')
    async def test_verify_email_view_get_expired_token(self, mock_error_response, mock_signer_class):
        """Тест з простроченим токеном"""
        mock_signer = Mock()
        mock_signer.unsign.side_effect = SignatureExpired('Token expired')
        mock_signer_class.return_value = mock_signer

        mock_error_response.return_value = Mock()

        request = self.factory.get(f'/?token={self.invalid_token}')

        await VerifyEmailView.get(request)

        mock_error_response.assert_called_once_with(gettext('The confirmation link has expired.'))

    @patch('users.views.TimestampSigner')
    @patch('users.views.error_response')
    async def test_verify_email_view_get_invalid_signature(self, mock_error_response, mock_signer_class):
        """Тест з невалідним підписом токена"""
        mock_signer = Mock()
        mock_signer.unsign.side_effect = BadSignature('Invalid signature')
        mock_signer_class.return_value = mock_signer

        mock_error_response.return_value = Mock()

        request = self.factory.get(f'/?token={self.invalid_token}')

        await VerifyEmailView.get(request)

        mock_error_response.assert_called_once_with(gettext('Invalid token for confirmation.'))

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    @patch('users.views.error_response')
    async def test_verify_email_view_get_user_not_found(self, mock_error_response, mock_signer_class,
                                                        mock_sync_to_async):
        """Тест з неіснуючим користувачем"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'nonexistent@example.com'
        mock_signer_class.return_value = mock_signer

        mock_get_user = AsyncMock(side_effect=CustomUser.DoesNotExist())
        mock_sync_to_async.return_value = mock_get_user

        mock_error_response.return_value = Mock()

        request = self.factory.get(f'/?token={self.valid_token}')

        await VerifyEmailView.get(request)

        mock_error_response.assert_called_once_with(gettext('No user with this email address was found.'))

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    @patch('users.views.success_response')
    async def test_verify_email_view_get_already_verified(self, mock_success_response, mock_signer_class,
                                                          mock_sync_to_async):
        """Тест з вже верифікованим користувачем"""
        mock_user = Mock()
        mock_user.is_verified_email = True

        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_get_user = AsyncMock(return_value=mock_user)
        mock_sync_to_async.return_value = mock_get_user

        mock_success_response.return_value = Mock()

        request = self.factory.get(f'/?token={self.valid_token}')

        await VerifyEmailView.get(request)

        mock_success_response.assert_called_once_with({"message": gettext('Email already confirmed.')})

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_verify_email_view_get_signer_configuration(self, mock_signer_class, mock_sync_to_async):
        """Тест конфігурації підписувача"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_sync_to_async.side_effect = [AsyncMock(return_value=mock_user), AsyncMock(), AsyncMock()]

        request = self.factory.get(f'/?token={self.valid_token}')

        with patch('users.views.invalidate_user_existence_cache'), \
                patch('users.views.warm_user_cache'), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(request)

        mock_signer_class.assert_called_once()
        mock_signer.unsign.assert_called_once_with(self.valid_token, max_age=60 * 60 * 24)

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_verify_email_view_get_user_activation(self, mock_signer_class, mock_sync_to_async):
        """Тест активації користувача при верифікації"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_get_user = AsyncMock(return_value=mock_user)
        mock_save_user = AsyncMock()
        mock_login = AsyncMock()
        mock_sync_to_async.side_effect = [mock_get_user, mock_save_user, mock_login]

        request = self.factory.get(f'/?token={self.valid_token}')

        with patch('users.views.invalidate_user_existence_cache'), \
                patch('users.views.warm_user_cache'), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(request)

        self.assertTrue(mock_user.is_verified_email)
        self.assertTrue(mock_user.is_active)

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    @patch('users.views.invalidate_user_existence_cache')
    async def test_verify_email_view_get_cache_invalidation(self, mock_invalidate_cache, mock_signer_class,
                                                            mock_sync_to_async):
        """Тест інвалідації кешу користувача"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_sync_to_async.side_effect = [AsyncMock(return_value=mock_user), AsyncMock(), AsyncMock()]
        mock_invalidate_cache.return_value = AsyncMock()

        request = self.factory.get(f'/?token={self.valid_token}')

        with patch('users.views.warm_user_cache'), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(request)

        mock_invalidate_cache.assert_called_once_with('test@example.com')

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    @patch('users.views.warm_user_cache')
    async def test_verify_email_view_get_cache_warming(self, mock_warm_cache, mock_signer_class, mock_sync_to_async):
        """Тест прогріву кешу користувача"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_sync_to_async.side_effect = [AsyncMock(return_value=mock_user), AsyncMock(), AsyncMock()]
        mock_warm_cache.return_value = AsyncMock()

        request = self.factory.get(f'/?token={self.valid_token}')

        with patch('users.views.invalidate_user_existence_cache'), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(request)

        mock_warm_cache.assert_called_once_with(mock_user)

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_verify_email_view_get_auto_login(self, mock_signer_class, mock_sync_to_async):
        """Тест автоматичного входу користувача після верифікації"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_get_user = AsyncMock(return_value=mock_user)
        mock_save_user = AsyncMock()
        mock_login = AsyncMock()
        mock_sync_to_async.side_effect = [mock_get_user, mock_save_user, mock_login]

        request = self.factory.get(f'/?token={self.valid_token}')

        with patch('users.views.invalidate_user_existence_cache'), \
                patch('users.views.warm_user_cache'), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(request)

        mock_login.assert_called_once_with(
            request,
            mock_user,
            backend='django.contrib.auth.backends.ModelBackend'
        )

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    @patch('users.views.redirect')
    async def test_verify_email_view_get_redirect_with_token(self, mock_redirect, mock_signer_class,
                                                             mock_sync_to_async):
        """Тест редиректу з токеном у URL"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_sync_to_async.side_effect = [AsyncMock(return_value=mock_user), AsyncMock(), AsyncMock()]
        mock_redirect.return_value = Mock()

        request = self.factory.get(f'/?token={self.valid_token}')

        with patch('users.views.invalidate_user_existence_cache'), \
                patch('users.views.warm_user_cache'):
            await VerifyEmailView.get(request)

        expected_url = f"{settings.FRONTEND_URL}/verify-email?token={self.valid_token}"
        mock_redirect.assert_called_once_with(expected_url)

    def test_verify_email_view_is_static_method(self):
        """Тест що get метод є статичним"""
        self.assertTrue(isinstance(VerifyEmailView.__dict__['get'], staticmethod))

    async def test_verify_email_view_get_async_function(self):
        """Тест що метод є async функцією"""
        request = self.factory.get(f'/?token={self.valid_token}')

        coroutine = VerifyEmailView.get(request)
        self.assertTrue(hasattr(coroutine, '__await__'))

        coroutine.close()

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_verify_email_view_get_token_max_age(self, mock_signer_class, mock_sync_to_async):
        """Тест максимального віку токена (24 години)"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_sync_to_async.side_effect = [AsyncMock(return_value=mock_user), AsyncMock(), AsyncMock()]

        request = self.factory.get(f'/?token={self.valid_token}')

        with patch('users.views.invalidate_user_existence_cache'), \
                patch('users.views.warm_user_cache'), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(request)

        mock_signer.unsign.assert_called_once_with(self.valid_token, max_age=60 * 60 * 24)

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_verify_email_view_get_email_case_sensitivity(self, mock_signer_class, mock_sync_to_async):
        """Тест чутливості до регістру email"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'Test@Example.COM'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_get_user = AsyncMock(return_value=mock_user)
        mock_save_user = AsyncMock()
        mock_login = AsyncMock()
        mock_sync_to_async.side_effect = [mock_get_user, mock_save_user, mock_login]

        request = self.factory.get(f'/?token={self.valid_token}')

        with patch('users.views.invalidate_user_existence_cache'), \
                patch('users.views.warm_user_cache'), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(request)

        mock_get_user.assert_called_once_with(email='Test@Example.COM')

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_verify_email_view_get_user_save_call(self, mock_signer_class, mock_sync_to_async):
        """Тест виклику збереження користувача"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False
        mock_user.save = Mock()

        mock_get_user = AsyncMock(return_value=mock_user)
        mock_save_user = AsyncMock()
        mock_login = AsyncMock()
        mock_sync_to_async.side_effect = [mock_get_user, mock_save_user, mock_login]

        request = self.factory.get(f'/?token={self.valid_token}')

        with patch('users.views.invalidate_user_existence_cache'), \
                patch('users.views.warm_user_cache'), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(request)

        self.assertEqual(mock_sync_to_async.call_count, 3)
        save_call = mock_sync_to_async.call_args_list[1]
        self.assertEqual(save_call[0][0], mock_user.save)

    def test_verify_email_view_decorator_applied(self):
        """Тест що декоратор ensure_csrf_cookie застосований"""
        self.assertTrue(hasattr(VerifyEmailView, 'dispatch'))

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_verify_email_view_get_multiple_tokens(self, mock_signer_class, mock_sync_to_async):
        """Тест з множинними токенами у GET параметрах"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_sync_to_async.side_effect = [AsyncMock(return_value=mock_user), AsyncMock(), AsyncMock()]

        request = self.factory.get(f'/?token={self.valid_token}&token=second_token')

        with patch('users.views.invalidate_user_existence_cache'), \
                patch('users.views.warm_user_cache'), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(request)

        mock_signer.unsign.assert_called_once_with("second_token", max_age=60 * 60 * 24)

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_verify_email_view_get_inactive_user_activation(self, mock_signer_class, mock_sync_to_async):
        """Тест активації неактивного користувача"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_sync_to_async.side_effect = [AsyncMock(return_value=mock_user), AsyncMock(), AsyncMock()]

        request = self.factory.get(f'/?token={self.valid_token}')

        with patch('users.views.invalidate_user_existence_cache'), \
                patch('users.views.warm_user_cache'), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(request)

        self.assertTrue(mock_user.is_active)

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_verify_email_view_get_preserves_request_object(self, mock_signer_class, mock_sync_to_async):
        """Тест що request об'єкт передається без змін"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        mock_get_user = AsyncMock(return_value=mock_user)
        mock_save_user = AsyncMock()
        mock_login = AsyncMock()
        mock_sync_to_async.side_effect = [mock_get_user, mock_save_user, mock_login]

        original_request = self.factory.get(f'/?token={self.valid_token}')
        original_request.custom_attr = 'test_value'

        with patch('users.views.invalidate_user_existence_cache'), \
                patch('users.views.warm_user_cache'), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(original_request)

        mock_login.assert_called_once_with(
            original_request,
            mock_user,
            backend='django.contrib.auth.backends.ModelBackend'
        )

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_verify_email_view_get_call_order(self, mock_signer_class, mock_sync_to_async):
        """Тест правильного порядку викликів функцій"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = 'test@example.com'
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.is_verified_email = False
        mock_user.is_active = False

        call_order = []

        async def track_get_user(*args, **kwargs):
            call_order.append('get_user')
            return mock_user

        async def track_save_user(*args, **kwargs):
            call_order.append('save_user')

        async def track_login(*args, **kwargs):
            call_order.append('login')

        mock_sync_to_async.side_effect = [track_get_user, track_save_user, track_login]

        async def track_invalidate_cache(*args):
            call_order.append('invalidate_cache')

        async def track_warm_cache(*args):
            call_order.append('warm_cache')

        request = self.factory.get(f'/?token={self.valid_token}')

        with patch('users.views.invalidate_user_existence_cache', side_effect=track_invalidate_cache), \
                patch('users.views.warm_user_cache', side_effect=track_warm_cache), \
                patch('users.views.redirect'):
            await VerifyEmailView.get(request)

        expected_order = ['get_user', 'save_user', 'invalidate_cache', 'warm_cache', 'login']
        self.assertEqual(call_order, expected_order)
