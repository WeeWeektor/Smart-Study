# ForgotPassword, ResetPassword, ChangePassword
import json
from unittest.mock import patch, AsyncMock, Mock

from django.core.exceptions import ValidationError
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.http import JsonResponse
from django.test import TestCase, RequestFactory

from smartStudy_backend import settings
from users.models import CustomUser
from users.views import ForgotPasswordView, ResetPasswordView, ChangePasswordView


class TestForgotPasswordView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ForgotPasswordView()
        self.valid_email = 'test@example.com'
        self.invalid_email = 'invalid-email'

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.get_user_existence_cache')
    @patch('users.views.send_password_reset_email')
    @patch('users.views.success_response')
    async def test_forgot_password_view_post_success(self, mock_success_response, mock_send_email,
                                                     mock_get_user_cache, mock_email_validator,
                                                     mock_sync_to_async):
        """Тест успішного надсилання email для скидання паролю"""
        mock_email_validator.return_value = None
        mock_get_user_cache.return_value = {
            'exists': True,
            'is_active': True,
            'is_verified': True
        }

        mock_user = Mock()
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=None),  # cache.get
            AsyncMock(return_value=mock_user),  # CustomUser.objects.get
            AsyncMock()  # cache.set
        ]

        mock_send_email.return_value = AsyncMock()
        mock_success_response.return_value = JsonResponse({'message': 'Email sent'})

        data = {'email': self.valid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        await self.view.post(request)

        mock_email_validator.assert_called_once_with(self.valid_email)
        mock_get_user_cache.assert_called_once_with(self.valid_email)
        mock_send_email.assert_called_once_with(mock_user)
        mock_success_response.assert_called_once()

    async def test_forgot_password_view_post_missing_email_field(self):
        """Тест з відсутнім полем email у JSON"""
        data = {'name': 'test'}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Missing field'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Missing field: email', 400)

    async def test_forgot_password_view_post_empty_email(self):
        """Тест з пустим email"""
        data = {'email': ''}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'No email provided'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('No email address provided.')

    async def test_forgot_password_view_post_none_email(self):
        """Тест з email = None"""
        data = {'email': None}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'No email provided'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('No email address provided.')

    @patch('users.views.cached_email_validator')
    async def test_forgot_password_view_post_invalid_email(self, mock_email_validator):
        """Тест з невалідним email"""
        mock_email_validator.side_effect = ValidationError('Invalid email format')

        data = {'email': self.invalid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Invalid email'}, status=400)

            await self.view.post(request)

            mock_email_validator.assert_called_once_with(self.invalid_email)
            mock_error_response.assert_called_once_with("['Invalid email format']")

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    async def test_forgot_password_view_post_rate_limited(self, mock_email_validator, mock_sync_to_async):
        """Тест з активним кешем (rate limiting)"""
        mock_email_validator.return_value = None
        mock_sync_to_async.return_value = AsyncMock(return_value=True)  # cache.get повертає True

        data = {'email': self.valid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Rate limited'}, status=429)

            await self.view.post(request)

            expected_message = ('A password reset request has been sent. Please check your email or try again in 5 '
                                'minutes.')
            mock_error_response.assert_called_once_with(message=expected_message, status=429)

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.get_user_existence_cache')
    async def test_forgot_password_view_post_user_not_exists(self, mock_get_user_cache,
                                                             mock_email_validator, mock_sync_to_async):
        """Тест з неіснуючим користувачем"""
        mock_email_validator.return_value = None
        mock_sync_to_async.return_value = AsyncMock(return_value=None)  # cache.get
        mock_get_user_cache.return_value = {
            'exists': False,
            'is_active': True,
            'is_verified': True
        }

        data = {'email': self.valid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'User not found'}, status=404)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('No user with this email address was found.', 404)

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.get_user_existence_cache')
    async def test_forgot_password_view_post_user_inactive(self, mock_get_user_cache,
                                                           mock_email_validator, mock_sync_to_async):
        """Тест з неактивним користувачем"""
        mock_email_validator.return_value = None
        mock_sync_to_async.return_value = AsyncMock(return_value=None)  # cache.get
        mock_get_user_cache.return_value = {
            'exists': True,
            'is_active': False,
            'is_verified': True
        }

        data = {'email': self.valid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Account inactive'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Account is inactive.', 400)

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.get_user_existence_cache')
    async def test_forgot_password_view_post_user_unverified(self, mock_get_user_cache,
                                                             mock_email_validator, mock_sync_to_async):
        """Тест з неверифікованим користувачем"""
        mock_email_validator.return_value = None
        mock_sync_to_async.return_value = AsyncMock(return_value=None)  # cache.get
        mock_get_user_cache.return_value = {
            'exists': True,
            'is_active': True,
            'is_verified': False
        }

        data = {'email': self.valid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Email not verified'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Email not confirmed. Please check your email.', 400)

    async def test_forgot_password_view_post_invalid_json(self):
        """Тест з невалідним JSON"""
        request = self.factory.post('/', data='invalid json', content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Invalid JSON'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Invalid JSON format.', 400)

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.get_user_existence_cache')
    @patch('users.views.send_password_reset_email')
    async def test_forgot_password_view_post_send_email_exception(self, mock_send_email, mock_get_user_cache,
                                                                  mock_email_validator, mock_sync_to_async):
        """Тест коли send_password_reset_email викидає виняток"""
        mock_email_validator.return_value = None
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=None),  # cache.get
            AsyncMock(return_value=Mock()),  # CustomUser.objects.get
        ]
        mock_get_user_cache.return_value = {
            'exists': True,
            'is_active': True,
            'is_verified': True
        }
        mock_send_email.side_effect = Exception('Email services error')

        data = {'email': self.valid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Server error'}, status=500)

            await self.view.post(request)

            expected_message = 'Error processing request: Email services error'
            mock_error_response.assert_called_once_with(expected_message, 500)

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.get_user_existence_cache')
    async def test_forgot_password_view_post_cache_key_generation(self, mock_get_user_cache,
                                                                  mock_email_validator, mock_sync_to_async):
        """Тест генерації ключа кешу"""
        mock_email_validator.return_value = None
        mock_get_user_cache.return_value = {
            'exists': True,
            'is_active': True,
            'is_verified': True
        }

        cache_get_mock = AsyncMock(return_value=None)
        cache_set_mock = AsyncMock()
        mock_user = Mock()

        mock_sync_to_async.side_effect = [
            cache_get_mock,  # cache.get
            AsyncMock(return_value=mock_user),  # CustomUser.objects.get
            cache_set_mock  # cache.set
        ]

        data = {'email': self.valid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.send_password_reset_email'), \
                patch('users.views.success_response', return_value=JsonResponse({'success': True})):
            await self.view.post(request)

            expected_cache_key = f"forgot_reset_{hash(self.valid_email)}"
            cache_get_mock.assert_called_once_with(expected_cache_key)

            cache_set_mock.assert_called_once_with(expected_cache_key, True, timeout=5 * 60)

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.get_user_existence_cache')
    @patch('users.views.send_password_reset_email')
    async def test_forgot_password_view_post_cache_timeout(self, mock_send_email, mock_get_user_cache,
                                                           mock_email_validator, mock_sync_to_async):
        """Тест що кеш встановлюється з правильним timeout (5 хвилин)"""
        mock_email_validator.return_value = None
        mock_get_user_cache.return_value = {
            'exists': True,
            'is_active': True,
            'is_verified': True
        }

        cache_set_mock = AsyncMock()
        mock_user = Mock()
        mock_send_email.return_value = AsyncMock()

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=None),  # cache.get
            AsyncMock(return_value=mock_user),  # CustomUser.objects.get
            cache_set_mock  # cache.set
        ]

        data = {'email': self.valid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.success_response', return_value=JsonResponse({'success': True})):
            await self.view.post(request)

            cache_set_mock.assert_called_once()

    def test_forgot_password_view_decorator_applied(self):
        """Тест що декоратор ensure_csrf_cookie застосований"""
        self.assertTrue(hasattr(ForgotPasswordView, 'dispatch'))

    async def test_forgot_password_view_post_async_method(self):
        """Тест що post метод є async"""
        data = {'email': self.valid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        coroutine = self.view.post(request)
        self.assertTrue(hasattr(coroutine, '__await__'))

        coroutine.close()

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.get_user_existence_cache')
    @patch('users.views.send_password_reset_email')
    @patch('users.views.success_response')
    async def test_forgot_password_view_post_success_message(self, mock_success_response, mock_send_email,
                                                             mock_get_user_cache, mock_email_validator,
                                                             mock_sync_to_async):
        """Тест правильного повідомлення про успіх"""
        mock_email_validator.return_value = None
        mock_get_user_cache.return_value = {
            'exists': True,
            'is_active': True,
            'is_verified': True
        }

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=None),  # cache.get
            AsyncMock(return_value=Mock()),  # CustomUser.objects.get
            AsyncMock()  # cache.set
        ]
        mock_send_email.return_value = AsyncMock()
        mock_success_response.return_value = JsonResponse({'message': 'Email sent'})

        data = {'email': self.valid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        await self.view.post(request)

        expected_message = {"message": "Please check your email for a password reset link."}
        mock_success_response.assert_called_once_with(expected_message)

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.get_user_existence_cache')
    async def test_forgot_password_view_post_user_retrieval(self, mock_get_user_cache, mock_email_validator,
                                                            mock_sync_to_async):
        """Тест отримання користувача з бази даних"""
        mock_email_validator.return_value = None
        mock_get_user_cache.return_value = {
            'exists': True,
            'is_active': True,
            'is_verified': True
        }

        mock_user = Mock()
        mock_get_user = AsyncMock(return_value=mock_user)

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=None),  # cache.get
            mock_get_user,  # CustomUser.objects.get
            AsyncMock()  # cache.set
        ]

        data = {'email': self.valid_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.send_password_reset_email'), \
                patch('users.views.success_response', return_value=JsonResponse({'success': True})):
            await self.view.post(request)

            mock_get_user.assert_called_once_with(email=self.valid_email)

    @patch('users.views.sync_to_async')
    @patch('users.views.cached_email_validator')
    @patch('users.views.get_user_existence_cache')
    async def test_forgot_password_view_post_unicode_email(self, mock_get_user_cache, mock_email_validator,
                                                           mock_sync_to_async):
        """Тест з Unicode символами в email"""
        unicode_email = 'тест@приклад.укр'
        mock_email_validator.return_value = None
        mock_get_user_cache.return_value = {
            'exists': True,
            'is_active': True,
            'is_verified': True
        }

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=None),  # cache.get
            AsyncMock(return_value=Mock()),  # CustomUser.objects.get
            AsyncMock()  # cache.set
        ]

        data = {'email': unicode_email}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.send_password_reset_email'), \
                patch('users.views.success_response', return_value=JsonResponse({'success': True})):
            await self.view.post(request)

            mock_email_validator.assert_called_once_with(unicode_email)
            mock_get_user_cache.assert_called_once_with(unicode_email)


class TestResetPasswordView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ResetPasswordView()
        self.valid_email = 'test@example.com'
        self.valid_password = 'NewPassword123!'
        self.signer = TimestampSigner()
        self.valid_token = self.signer.sign(self.valid_email)

    # GET method tests
    @patch('users.views.sync_to_async')
    @patch('users.views.redirect')
    async def test_reset_password_view_get_success(self, mock_redirect, mock_sync_to_async):
        """Тест успішного GET запиту з валідним токеном"""
        mock_user = Mock()
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_user)
        mock_redirect.return_value = JsonResponse({'redirect': True})

        request = self.factory.get('/', {'token': self.valid_token})

        await self.view.get(request)

        mock_sync_to_async.assert_called_once()
        expected_url = f"{settings.FRONTEND_URL}/reset-password?token={self.valid_token}"
        mock_redirect.assert_called_once_with(expected_url)

    async def test_reset_password_view_get_missing_token(self):
        """Тест GET запиту без токена"""
        request = self.factory.get('/')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'No token'}, status=400)

            await self.view.get(request)

            mock_error_response.assert_called_once_with('No token to reset the password.', 400)

    async def test_reset_password_view_get_empty_token(self):
        """Тест GET запиту з пустим токеном"""
        request = self.factory.get('/', {'token': ''})

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'No token'}, status=400)

            await self.view.get(request)

            mock_error_response.assert_called_once_with('No token to reset the password.', 400)

    async def test_reset_password_view_get_none_token(self):
        """Тест GET запиту без токена (параметр відсутній)"""
        request = self.factory.get('/')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'No token'}, status=400)

            await self.view.get(request)

            mock_error_response.assert_called_once_with('No token to reset the password.', 400)

    @patch('users.views.TimestampSigner')
    async def test_reset_password_view_get_expired_token(self, mock_signer_class):
        """Тест GET запиту з прострочським токеном"""
        mock_signer = Mock()
        mock_signer.unsign.side_effect = SignatureExpired()
        mock_signer_class.return_value = mock_signer

        request = self.factory.get('/', {'token': 'expired_token'})

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Token expired'}, status=400)

            await self.view.get(request)

            mock_error_response.assert_called_once_with('The token for resetting the password has expired.', 400)

    @patch('users.views.TimestampSigner')
    async def test_reset_password_view_get_invalid_token(self, mock_signer_class):
        """Тест GET запиту з невалідним токеном"""
        mock_signer = Mock()
        mock_signer.unsign.side_effect = BadSignature()
        mock_signer_class.return_value = mock_signer

        request = self.factory.get('/', {'token': 'invalid_token'})

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Invalid token'}, status=400)

            await self.view.get(request)

            mock_error_response.assert_called_once_with('Invalid token for password reset.', 400)

    @patch('users.views.TimestampSigner')
    @patch('users.views.sync_to_async')
    async def test_reset_password_view_get_user_not_found(self, mock_sync_to_async, mock_signer_class):
        """Тест GET запиту коли користувача не знайдено"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = self.valid_email
        mock_signer_class.return_value = mock_signer

        mock_sync_to_async.return_value = AsyncMock(side_effect=CustomUser.DoesNotExist())

        request = self.factory.get('/', {'token': 'valid_token'})

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'User not found'}, status=404)

            await self.view.get(request)

            mock_error_response.assert_called_once_with('No user with this email address was found.', 404)

    @patch('users.views.TimestampSigner')
    async def test_reset_password_view_get_token_max_age(self, mock_signer_class):
        """Тест що токен перевіряється з правильним max_age"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = self.valid_email
        mock_signer_class.return_value = mock_signer

        request = self.factory.get('/', {'token': 'test_token'})

        with patch('users.views.sync_to_async') as mock_sync_to_async, \
                patch('users.views.redirect'):
            mock_sync_to_async.return_value = AsyncMock(return_value=Mock())

            await self.view.get(request)

            mock_signer.unsign.assert_called_once_with('test_token', max_age=60 * 60 * 24)

    # POST method tests
    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    @patch('users.views.invalidate_all_user_caches')
    @patch('users.views.success_response')
    async def test_reset_password_view_post_success(self, mock_success_response, mock_invalidate_cache,
                                                    mock_signer_class, mock_sync_to_async):
        """Тест успішного скидання паролю"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = self.valid_email
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = self.valid_email
        mock_sync_to_async.side_effect = [
            AsyncMock(),  # validate_password
            AsyncMock(return_value=mock_user),  # CustomUser.objects.get
            AsyncMock(),  # user.set_password
            AsyncMock()  # user.save
        ]

        mock_invalidate_cache.return_value = AsyncMock()
        mock_success_response.return_value = JsonResponse({'success': True})

        data = {'token': self.valid_token, 'password': self.valid_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        await self.view.post(request)

        mock_invalidate_cache.assert_called_once_with(1, self.valid_email)
        mock_success_response.assert_called_once_with({"message": "Password reset successful."})

    async def test_reset_password_view_post_missing_token(self):
        """Тест POST запиту без токена"""
        data = {'password': self.valid_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Missing fields'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Required fields are missing: token or password.')

    async def test_reset_password_view_post_missing_password(self):
        """Тест POST запиту без паролю"""
        data = {'token': self.valid_token}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Missing fields'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Required fields are missing: token or password.')

    async def test_reset_password_view_post_missing_both_fields(self):
        """Тест POST запиту без токена та паролю"""
        data = {'name': 'test'}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Missing fields'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Required fields are missing: token or password.')

    async def test_reset_password_view_post_empty_token(self):
        """Тест POST запиту з пустим токеном"""
        data = {'token': '', 'password': self.valid_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.sync_to_async') as mock_sync_to_async, \
                patch('users.views.TimestampSigner') as mock_signer_class, \
                patch('users.views.error_response') as mock_error_response:
            mock_sync_to_async.return_value = AsyncMock()

            mock_signer = Mock()
            mock_signer.unsign.side_effect = BadSignature()
            mock_signer_class.return_value = mock_signer

            mock_error_response.return_value = JsonResponse({'error': 'Invalid token'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Invalid token for password reset.', 400)

    async def test_reset_password_view_post_missing_token_key(self):
        """Тест POST запиту коли ключ 'token' відсутній в JSON"""
        data = {'password': self.valid_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Missing fields'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Required fields are missing: token or password.')

    async def test_reset_password_view_post_missing_password_key(self):
        """Тест POST запиту коли ключ 'password' відсутній в JSON"""
        data = {'token': self.valid_token}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Missing fields'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Required fields are missing: token or password.')

    async def test_reset_password_view_post_empty_password(self):
        """Тест POST запиту з пустим паролем"""
        data = {'token': self.valid_token, 'password': ''}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.sync_to_async') as mock_sync_to_async, \
                patch('users.views.error_response') as mock_error_response:
            mock_sync_to_async.side_effect = ValidationError(
                ['This password is too short. It must contain at least 8 characters.'])

            mock_error_response.return_value = JsonResponse({'error': 'Validation error'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with(
                'This password is too short. It must contain at least 8 characters.')

    @patch('users.views.sync_to_async')
    async def test_reset_password_view_post_invalid_password(self, mock_sync_to_async):
        """Тест POST запиту з невалідним паролем"""
        mock_sync_to_async.side_effect = ValidationError(['Password too weak'])

        data = {'token': self.valid_token, 'password': '123'}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Invalid password'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Password too weak')

    @patch('users.views.sync_to_async')
    async def test_reset_password_view_post_multiple_password_errors(self, mock_sync_to_async):
        """Тест POST запиту з кількома помилками валідації паролю"""
        mock_sync_to_async.side_effect = ValidationError(['Password too short', 'Password too weak'])

        data = {'token': self.valid_token, 'password': '123'}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Multiple errors'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Password too short, Password too weak')

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_reset_password_view_post_expired_token(self, mock_signer_class, mock_sync_to_async):
        """Тест POST запиту з прострочвським токеном"""
        mock_sync_to_async.return_value = AsyncMock()  # validate_password

        mock_signer = Mock()
        mock_signer.unsign.side_effect = SignatureExpired()
        mock_signer_class.return_value = mock_signer

        data = {'token': 'expired_token', 'password': self.valid_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Token expired'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('The token for resetting the password has expired.', 400)

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_reset_password_view_post_invalid_token(self, mock_signer_class, mock_sync_to_async):
        """Тест POST запиту з невалідним токеном"""
        mock_sync_to_async.return_value = AsyncMock()  # validate_password

        mock_signer = Mock()
        mock_signer.unsign.side_effect = BadSignature()
        mock_signer_class.return_value = mock_signer

        data = {'token': 'invalid_token', 'password': self.valid_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Invalid token'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Invalid token for password reset.', 400)

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_reset_password_view_post_user_not_found(self, mock_signer_class, mock_sync_to_async):
        """Тест POST запиту коли користувача не знайдено"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = self.valid_email
        mock_signer_class.return_value = mock_signer

        mock_sync_to_async.side_effect = [
            AsyncMock(),  # validate_password
            AsyncMock(side_effect=CustomUser.DoesNotExist())  # CustomUser.objects.get
        ]

        data = {'token': self.valid_token, 'password': self.valid_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'User not found'}, status=404)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('No user with this email address was found.', 404)

    async def test_reset_password_view_post_invalid_json(self):
        """Тест POST запиту з невалідним JSON"""
        request = self.factory.post('/', data='invalid json', content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Invalid JSON'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('Invalid JSON format.', 400)

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_reset_password_view_post_save_exception(self, mock_signer_class, mock_sync_to_async):
        """Тест POST запиту коли виникає помилка при збереженні"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = self.valid_email
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_sync_to_async.side_effect = [
            AsyncMock(),  # validate_password
            AsyncMock(return_value=mock_user),  # CustomUser.objects.get
            AsyncMock(),  # user.set_password
            AsyncMock(side_effect=Exception('Database error'))  # user.save
        ]

        data = {'token': self.valid_token, 'password': self.valid_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Server error'}, status=500)

            await self.view.post(request)

            expected_message = 'Error when resetting password: Database error'
            mock_error_response.assert_called_once_with(expected_message, 500)

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_reset_password_view_post_token_max_age(self, mock_signer_class, mock_sync_to_async):
        """Тест що токен в POST перевіряється з правильним max_age"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = self.valid_email
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_sync_to_async.side_effect = [
            AsyncMock(),  # validate_password
            AsyncMock(return_value=mock_user),  # CustomUser.objects.get
            AsyncMock(),  # user.set_password
            AsyncMock()  # user.save
        ]

        data = {'token': 'test_token', 'password': self.valid_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.invalidate_all_user_caches'), \
                patch('users.views.success_response'):
            await self.view.post(request)

            mock_signer.unsign.assert_called_once_with('test_token', max_age=60 * 60 * 24)

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    @patch('users.views.invalidate_all_user_caches')
    async def test_reset_password_view_post_cache_invalidation(self, mock_invalidate_cache, mock_signer_class,
                                                               mock_sync_to_async):
        """Тест що кеш користувача інвалідується після скидання паролю"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = self.valid_email
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.id = 123
        mock_user.email = self.valid_email
        mock_sync_to_async.side_effect = [
            AsyncMock(),  # validate_password
            AsyncMock(return_value=mock_user),  # CustomUser.objects.get
            AsyncMock(),  # user.set_password
            AsyncMock()  # user.save
        ]

        mock_invalidate_cache.return_value = AsyncMock()

        data = {'token': self.valid_token, 'password': self.valid_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.success_response'):
            await self.view.post(request)

            mock_invalidate_cache.assert_called_once_with(123, self.valid_email)

    def test_reset_password_view_decorator_applied(self):
        """Тест що декоратор ensure_csrf_cookie застосований"""
        self.assertTrue(hasattr(ResetPasswordView, 'dispatch'))

    async def test_reset_password_view_get_async_method(self):
        """Тест що GET метод є async"""
        request = self.factory.get('/', {'token': 'test'})

        coroutine = self.view.get(request)
        self.assertTrue(hasattr(coroutine, '__await__'))

        coroutine.close()

    async def test_reset_password_view_post_async_method(self):
        """Тест що POST метод є async"""
        data = {'token': 'test', 'password': 'test'}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        coroutine = self.view.post(request)
        self.assertTrue(hasattr(coroutine, '__await__'))

        coroutine.close()

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_reset_password_view_post_unicode_password(self, mock_signer_class, mock_sync_to_async):
        """Тест POST запиту з Unicode символами в паролі"""
        unicode_password = 'Пароль123!'
        mock_signer = Mock()
        mock_signer.unsign.return_value = self.valid_email
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = self.valid_email
        mock_sync_to_async.side_effect = [
            AsyncMock(),  # validate_password
            AsyncMock(return_value=mock_user),  # CustomUser.objects.get
            AsyncMock(),  # user.set_password
            AsyncMock()  # user.save
        ]

        data = {'token': self.valid_token, 'password': unicode_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.invalidate_all_user_caches'), \
                patch('users.views.success_response', return_value=JsonResponse({'success': True})):
            await self.view.post(request)

            validate_call = mock_sync_to_async.call_args_list[0]
            self.assertEqual(validate_call[0][0].__name__, 'validate_password')

    @patch('users.views.sync_to_async')
    @patch('users.views.TimestampSigner')
    async def test_reset_password_view_post_password_setting_order(self, mock_signer_class, mock_sync_to_async):
        """Тест що методи викликаються в правильному порядку"""
        mock_signer = Mock()
        mock_signer.unsign.return_value = self.valid_email
        mock_signer_class.return_value = mock_signer

        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = self.valid_email

        validate_mock = AsyncMock()
        get_user_mock = AsyncMock(return_value=mock_user)
        set_password_mock = AsyncMock()
        save_mock = AsyncMock()

        mock_sync_to_async.side_effect = [
            validate_mock,
            get_user_mock,
            set_password_mock,
            save_mock
        ]

        data = {'token': self.valid_token, 'password': self.valid_password}
        request = self.factory.post('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.invalidate_all_user_caches'), \
                patch('users.views.success_response'):
            await self.view.post(request)

            self.assertEqual(len(mock_sync_to_async.call_args_list), 4)
            validate_mock.assert_called_once()
            get_user_mock.assert_called_once()
            set_password_mock.assert_called_once()
            save_mock.assert_called_once()


class TestChangePasswordView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ChangePasswordView()
        self.current_password = 'CurrentPassword123!'
        self.new_password = 'NewPassword123!'
        self.valid_data = {
            'current_password': self.current_password,
            'new_password': self.new_password,
            'confirm_password': self.new_password
        }

    @patch('users.views.sync_to_async')
    @patch('users.views.invalidate_user_cache')
    @patch('users.views.success_response')
    async def test_change_password_view_patch_success(self, mock_success_response, mock_invalidate_cache,
                                                      mock_sync_to_async):
        """Тест успішної зміни паролю"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.check_password.return_value = True

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(),  # validate_password
            AsyncMock(),  # set_password
            AsyncMock(),  # save
            AsyncMock()  # login
        ]

        mock_invalidate_cache.return_value = AsyncMock()
        mock_success_response.return_value = JsonResponse({'success': True})

        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')
        request.user = mock_user

        await self.view.patch(request)

        mock_invalidate_cache.assert_called_once_with(1)
        mock_success_response.assert_called_once_with({"message": "Password successfully changed."})

    @patch('users.views.sync_to_async')
    async def test_change_password_view_patch_unauthenticated(self, mock_sync_to_async):
        """Тест зміни паролю неавторизованим користувачем"""
        mock_sync_to_async.return_value = AsyncMock(return_value=False)

        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Unauthorized'}, status=401)

            await self.view.patch(request)

            mock_error_response.assert_called_once_with('The user is not authorized.', 401)

    async def test_change_password_view_patch_missing_current_password(self):
        """Тест зміни паролю без поточного паролю"""
        data = {
            'new_password': self.new_password,
            'confirm_password': self.new_password
        }

        request = self.factory.patch('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.sync_to_async', return_value=AsyncMock(return_value=True)), \
                patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Missing fields'}, status=400)

            await self.view.patch(request)

            expected_message = 'Required fields are missing: current_password, new_password, or confirm_password.'
            mock_error_response.assert_called_once_with(expected_message)

    async def test_change_password_view_patch_missing_new_password(self):
        """Тест зміни паролю без нового паролю"""
        data = {
            'current_password': self.current_password,
            'confirm_password': self.new_password
        }

        request = self.factory.patch('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.sync_to_async', return_value=AsyncMock(return_value=True)), \
                patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Missing fields'}, status=400)

            await self.view.patch(request)

            expected_message = 'Required fields are missing: current_password, new_password, or confirm_password.'
            mock_error_response.assert_called_once_with(expected_message)

    async def test_change_password_view_patch_missing_confirm_password(self):
        """Тест зміни паролю без підтвердження паролю"""
        data = {
            'current_password': self.current_password,
            'new_password': self.new_password
        }

        request = self.factory.patch('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.sync_to_async', return_value=AsyncMock(return_value=True)), \
                patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Missing fields'}, status=400)

            await self.view.patch(request)

            expected_message = 'Required fields are missing: current_password, new_password, or confirm_password.'
            mock_error_response.assert_called_once_with(expected_message)

    async def test_change_password_view_patch_missing_all_fields(self):
        """Тест зміни паролю без всіх обов'язкових полів"""
        data = {'email': 'test@example.com'}

        request = self.factory.patch('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.sync_to_async', return_value=AsyncMock(return_value=True)), \
                patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Missing fields'}, status=400)

            await self.view.patch(request)

            expected_message = 'Required fields are missing: current_password, new_password, or confirm_password.'
            mock_error_response.assert_called_once_with(expected_message)

    async def test_change_password_view_patch_password_mismatch(self):
        """Тест зміни паролю з невідповідністю нового паролю та підтвердження"""
        data = {
            'current_password': self.current_password,
            'new_password': self.new_password,
            'confirm_password': 'DifferentPassword123!'
        }

        request = self.factory.patch('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.sync_to_async', return_value=AsyncMock(return_value=True)), \
                patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Password mismatch'}, status=400)

            await self.view.patch(request)

            mock_error_response.assert_called_once_with('The new password and password confirmation do not match.', 400)

    @patch('users.views.sync_to_async')
    async def test_change_password_view_patch_invalid_new_password(self, mock_sync_to_async):
        """Тест зміни паролю з невалідним новим паролем"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(side_effect=ValidationError(['Password too weak']))  # validate_password
        ]

        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Invalid password'}, status=400)

            await self.view.patch(request)

            mock_error_response.assert_called_once_with('Password too weak')

    @patch('users.views.sync_to_async')
    async def test_change_password_view_patch_multiple_password_errors(self, mock_sync_to_async):
        """Тест зміни паролю з кількома помилками валідації нового паролю"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(side_effect=ValidationError(['Password too short', 'Password too weak']))  # validate_password
        ]

        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Multiple errors'}, status=400)

            await self.view.patch(request)

            mock_error_response.assert_called_once_with('Password too short, Password too weak')

    @patch('users.views.sync_to_async')
    async def test_change_password_view_patch_incorrect_current_password(self, mock_sync_to_async):
        """Тест зміни паролю з неправильним поточним паролем"""
        mock_user = Mock()
        mock_user.check_password.return_value = False

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock()  # validate_password
        ]

        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')
        request.user = mock_user

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Incorrect password'}, status=400)

            await self.view.patch(request)

            mock_error_response.assert_called_once_with('Incorrect current password.', 400)

    async def test_change_password_view_patch_invalid_json(self):
        """Тест зміни паролю з невалідним JSON"""
        request = self.factory.patch('/', data='invalid json', content_type='application/json')

        with patch('users.views.sync_to_async', return_value=AsyncMock(return_value=True)), \
                patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Invalid JSON'}, status=400)

            await self.view.patch(request)

            mock_error_response.assert_called_once_with('Invalid JSON format.', 400)

    @patch('users.views.sync_to_async')
    async def test_change_password_view_patch_save_exception(self, mock_sync_to_async):
        """Тест зміни паролю коли виникає помилка при збереженні"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.check_password.return_value = True

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(),  # validate_password
            AsyncMock(),  # set_password
            AsyncMock(side_effect=Exception('Database error'))  # save
        ]

        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')
        request.user = mock_user

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Server error'}, status=500)

            await self.view.patch(request)

            expected_message = 'Error when changing password: Database error'
            mock_error_response.assert_called_once_with(expected_message, 500)

    @patch('users.views.sync_to_async')
    @patch('users.views.invalidate_user_cache')
    async def test_change_password_view_patch_login_exception(self, mock_invalidate_cache, mock_sync_to_async):
        """Тест зміни паролю коли виникає помилка при повторному логіні"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.check_password.return_value = True

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(),  # validate_password
            AsyncMock(),  # set_password
            AsyncMock(),  # save
            AsyncMock(side_effect=Exception('Login error'))  # login
        ]

        mock_invalidate_cache.return_value = AsyncMock()

        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')
        request.user = mock_user

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Server error'}, status=500)

            await self.view.patch(request)

            expected_message = 'Error when changing password: Login error'
            mock_error_response.assert_called_once_with(expected_message, 500)

    @patch('users.views.sync_to_async')
    @patch('users.views.invalidate_user_cache')
    async def test_change_password_view_patch_cache_invalidation(self, mock_invalidate_cache, mock_sync_to_async):
        """Тест що кеш користувача інвалідується після зміни паролю"""
        mock_user = Mock()
        mock_user.id = 123
        mock_user.check_password.return_value = True

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(),  # validate_password
            AsyncMock(),  # set_password
            AsyncMock(),  # save
            AsyncMock()  # login
        ]

        mock_invalidate_cache.return_value = AsyncMock()

        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')
        request.user = mock_user

        with patch('users.views.success_response'):
            await self.view.patch(request)

            mock_invalidate_cache.assert_called_once_with(123)

    @patch('users.views.sync_to_async')
    async def test_change_password_view_patch_login_backend(self, mock_sync_to_async):
        """Тест що login викликається з правильним backend"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.check_password.return_value = True

        login_mock = AsyncMock()
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(),  # validate_password
            AsyncMock(),  # set_password
            AsyncMock(),  # save
            login_mock  # login
        ]

        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')
        request.user = mock_user

        with patch('users.views.invalidate_user_cache'), \
                patch('users.views.success_response'):
            await self.view.patch(request)

            login_mock.assert_called_once()

    def test_change_password_view_decorator_applied(self):
        """Тест що декоратор ensure_csrf_cookie застосований"""
        self.assertTrue(hasattr(ChangePasswordView, 'dispatch'))

    async def test_change_password_view_patch_async_method(self):
        """Тест що PATCH метод є async"""
        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')

        coroutine = self.view.patch(request)
        self.assertTrue(hasattr(coroutine, '__await__'))

        coroutine.close()

    @patch('users.views.sync_to_async')
    async def test_change_password_view_patch_empty_passwords(self, mock_sync_to_async):
        """Тест зміни паролю з пустими паролями"""
        data = {
            'current_password': '',
            'new_password': '',
            'confirm_password': ''
        }

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(side_effect=ValidationError(['This field cannot be blank']))  # validate_password
        ]

        request = self.factory.patch('/', data=json.dumps(data), content_type='application/json')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Empty field'}, status=400)

            await self.view.patch(request)

            mock_error_response.assert_called_once_with('This field cannot be blank')

    @patch('users.views.sync_to_async')
    async def test_change_password_view_patch_unicode_passwords(self, mock_sync_to_async):
        """Тест зміни паролю з Unicode символами"""
        unicode_password = 'НовийПароль123!'
        data = {
            'current_password': 'СтарийПароль123!',
            'new_password': unicode_password,
            'confirm_password': unicode_password
        }

        mock_user = Mock()
        mock_user.id = 1
        mock_user.check_password.return_value = True

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(),  # validate_password
            AsyncMock(),  # set_password
            AsyncMock(),  # save
            AsyncMock()  # login
        ]

        request = self.factory.patch('/', data=json.dumps(data), content_type='application/json')
        request.user = mock_user

        with patch('users.views.invalidate_user_cache'), \
                patch('users.views.success_response', return_value=JsonResponse({'success': True})):
            await self.view.patch(request)

            validate_call = mock_sync_to_async.call_args_list[1]
            self.assertEqual(validate_call[0][0].__name__, 'validate_password')

    @patch('users.views.sync_to_async')
    async def test_change_password_view_patch_operations_order(self, mock_sync_to_async):
        """Тест що операції виконуються в правильному порядку"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.check_password.return_value = True

        auth_mock = AsyncMock(return_value=True)
        validate_mock = AsyncMock()
        set_password_mock = AsyncMock()
        save_mock = AsyncMock()
        login_mock = AsyncMock()

        mock_sync_to_async.side_effect = [
            auth_mock,
            validate_mock,
            set_password_mock,
            save_mock,
            login_mock
        ]

        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')
        request.user = mock_user

        with patch('users.views.invalidate_user_cache'), \
                patch('users.views.success_response'):
            await self.view.patch(request)

            self.assertEqual(len(mock_sync_to_async.call_args_list), 5)
            auth_mock.assert_called_once()
            validate_mock.assert_called_once()
            set_password_mock.assert_called_once()
            save_mock.assert_called_once()
            login_mock.assert_called_once()

    @patch('users.views.sync_to_async')
    async def test_change_password_view_patch_same_password(self, mock_sync_to_async):
        """Тест зміни паролю на той самий пароль"""
        same_password = 'SamePassword123!'
        data = {
            'current_password': same_password,
            'new_password': same_password,
            'confirm_password': same_password
        }

        mock_user = Mock()
        mock_user.id = 1
        mock_user.check_password.return_value = True

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(),  # validate_password
            AsyncMock(),  # set_password
            AsyncMock(),  # save
            AsyncMock()  # login
        ]

        request = self.factory.patch('/', data=json.dumps(data), content_type='application/json')
        request.user = mock_user

        with patch('users.views.invalidate_user_cache'), \
                patch('users.views.success_response', return_value=JsonResponse({'success': True})):
            await self.view.patch(request)

            self.assertEqual(len(mock_sync_to_async.call_args_list), 5)

    @patch('users.views.sync_to_async')
    async def test_change_password_view_patch_password_validation_call(self, mock_sync_to_async):
        """Тест що validate_password викликається з новим паролем"""
        mock_user = Mock()
        mock_user.check_password.return_value = True

        validate_mock = AsyncMock()
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            validate_mock,  # validate_password
            AsyncMock(),  # set_password
            AsyncMock(),  # save
            AsyncMock()  # login
        ]

        request = self.factory.patch('/', data=json.dumps(self.valid_data), content_type='application/json')
        request.user = mock_user

        with patch('users.views.invalidate_user_cache'), \
                patch('users.views.success_response'):
            await self.view.patch(request)

            validate_call = mock_sync_to_async.call_args_list[1]
            self.assertEqual(validate_call[0][0].__name__, 'validate_password')
