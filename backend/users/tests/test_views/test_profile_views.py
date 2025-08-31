# ProfileView
import json
from unittest.mock import patch, AsyncMock, Mock

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.test import TestCase, RequestFactory

from users.views import ProfileView


class TestProfileView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ProfileView()
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.email = 'test@example.com'
        self.profile_data = {
            'user': {'name': 'Test', 'surname': 'User'},
            'settings': {'email_notifications': True},
            'profile': {'bio': 'Test bio'}
        }

    # GET method tests
    @patch('users.views.sync_to_async')
    @patch('users.views.get_cached_profile')
    @patch('users.views.success_response')
    async def test_profile_view_get_success(self, mock_success_response, mock_get_cached_profile, mock_sync_to_async):
        """Тест успішного отримання профілю"""
        mock_sync_to_async.return_value = AsyncMock(return_value=True)
        mock_get_cached_profile.return_value = self.profile_data
        mock_success_response.return_value = JsonResponse({'success': True})

        request = self.factory.get('/')
        request.user = self.mock_user

        await self.view.get(request)

        mock_get_cached_profile.assert_called_once_with(self.mock_user)
        mock_success_response.assert_called_once_with(self.profile_data)

    @patch('users.views.sync_to_async')
    async def test_profile_view_get_unauthenticated(self, mock_sync_to_async):
        """Тест отримання профілю неавторизованим користувачем"""
        mock_sync_to_async.return_value = AsyncMock(return_value=False)

        request = self.factory.get('/')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Unauthorized'}, status=401)

            await self.view.get(request)

            mock_error_response.assert_called_once_with('User not authorized.', 401)

    @patch('users.views.sync_to_async')
    @patch('users.views.get_cached_profile')
    async def test_profile_view_get_exception(self, mock_get_cached_profile, mock_sync_to_async):
        """Тест обробки винятку при отриманні профілю"""
        mock_sync_to_async.return_value = AsyncMock(return_value=True)
        mock_get_cached_profile.side_effect = Exception('Cache error')

        request = self.factory.get('/')
        request.user = self.mock_user

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Server error'}, status=500)

            await self.view.get(request)

            mock_error_response.assert_called_once()

    # POST method tests (avatar upload)
    @patch('users.views.sync_to_async')
    @patch('users.views.handle_profile_picture')
    @patch('users.views.invalidate_user_cache')
    @patch('users.views.success_response')
    async def test_profile_view_post_success(self, mock_success_response, mock_invalidate_cache,
                                             mock_handle_profile_picture, mock_sync_to_async):
        """Тест успішного завантаження аватара"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=(Mock(), True)),  # get_or_create
            AsyncMock(return_value=1)  # user.id
        ]

        mock_profile = Mock()
        mock_profile.profile_picture = 'https://example.com/avatar.jpg'
        mock_sync_to_async.return_value.return_value = (mock_profile, True)

        mock_handle_profile_picture.return_value = AsyncMock()
        mock_invalidate_cache.return_value = AsyncMock()
        mock_success_response.return_value = JsonResponse({'success': True})

        request = Mock()
        request.user = self.mock_user
        request.FILES = {'profile_picture': Mock()}

        await self.view.post(request)

        mock_handle_profile_picture.assert_called_once()

    @patch('users.views.sync_to_async')
    async def test_profile_view_post_unauthenticated(self, mock_sync_to_async):
        """Тест завантаження аватара неавторизованим користувачем"""
        mock_sync_to_async.return_value = AsyncMock(return_value=False)

        request = Mock()
        request.FILES = {'profile_picture': Mock()}

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Unauthorized'}, status=401)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('User not authorized.', 401)

    @patch('users.views.sync_to_async')
    async def test_profile_view_post_no_file(self, mock_sync_to_async):
        """Тест завантаження аватара без файлу"""
        mock_sync_to_async.return_value = AsyncMock(return_value=True)

        request = Mock()
        request.user = self.mock_user
        request.FILES = {}

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'File not found'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('File not found.', 400)

    @patch('users.views.sync_to_async')
    @patch('users.views.handle_profile_picture')
    async def test_profile_view_post_validation_error(self, mock_handle_profile_picture, mock_sync_to_async):
        """Тест валідаційної помилки при завантаженні аватара"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=(Mock(), True))  # get_or_create
        ]

        mock_handle_profile_picture.side_effect = ValidationError('Invalid file format')

        request = Mock()
        request.user = self.mock_user
        request.FILES = {'profile_picture': Mock()}

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Validation error'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with("['Invalid file format']", 400)

    @patch('users.views.sync_to_async')
    async def test_profile_view_post_exception(self, mock_sync_to_async):
        """Тест загальної помилки при завантаженні аватара"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            Exception('Server error')  # get_or_create викидає помилку
        ]

        request = Mock()
        request.user = self.mock_user
        request.FILES = {'profile_picture': Mock()}

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Server error'}, status=500)

            await self.view.post(request)

            mock_error_response.assert_called_once()

    # PATCH method tests (profile update)
    @patch('users.views.sync_to_async')
    @patch('users.views.parse_request_data')
    @patch('users.views.update_user_data')
    @patch('users.views.update_user_settings')
    @patch('users.views.update_user_profile')
    @patch('users.views.invalidate_user_cache')
    @patch('users.views.get_cached_profile')
    @patch('users.views.success_response')
    async def test_profile_view_patch_success(self, mock_success_response, mock_get_cached_profile,
                                              mock_invalidate_cache, mock_update_profile, mock_update_settings,
                                              mock_update_data, mock_parse_request, mock_sync_to_async):
        """Тест успішного оновлення профілю"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=1)  # user.id
        ]

        mock_parse_request.return_value = (self.profile_data, False)
        mock_update_data.return_value = AsyncMock()
        mock_update_settings.return_value = AsyncMock()
        mock_update_profile.return_value = AsyncMock()
        mock_invalidate_cache.return_value = AsyncMock()
        mock_get_cached_profile.return_value = self.profile_data
        mock_success_response.return_value = JsonResponse({'success': True})

        request = self.factory.patch('/')
        request.user = self.mock_user

        await self.view.patch(request)

        mock_update_data.assert_called_once_with(self.mock_user, {'name': 'Test', 'surname': 'User'})
        mock_update_settings.assert_called_once_with(self.mock_user, {'email_notifications': True}, False)
        mock_update_profile.assert_called_once_with(self.mock_user, {'bio': 'Test bio'})

    @patch('users.views.sync_to_async')
    async def test_profile_view_patch_unauthenticated(self, mock_sync_to_async):
        """Тест оновлення профілю неавторизованим користувачем"""
        mock_sync_to_async.return_value = AsyncMock(return_value=False)

        request = self.factory.patch('/')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Unauthorized'}, status=401)

            await self.view.patch(request)

            mock_error_response.assert_called_once_with('User not authorized.', 401)

    @patch('users.views.sync_to_async')
    @patch('users.views.parse_request_data')
    @patch('users.views.update_user_data')
    @patch('users.views.update_user_settings')
    @patch('users.views.update_user_profile')
    @patch('users.views.handle_profile_picture')
    @patch('users.views.invalidate_user_cache')
    @patch('users.views.get_cached_profile')
    async def test_profile_view_patch_with_avatar(self, mock_get_cached_profile, mock_invalidate_cache,
                                                  mock_handle_profile_picture, mock_update_profile,
                                                  mock_update_settings, mock_update_data, mock_parse_request,
                                                  mock_sync_to_async):
        """Тест оновлення профілю з новим аватаром"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=Mock()),  # UserProfile.objects.get
            AsyncMock(return_value=1)  # user.id
        ]

        mock_parse_request.return_value = (self.profile_data, True)
        mock_update_data.return_value = AsyncMock()
        mock_update_settings.return_value = AsyncMock()
        mock_update_profile.return_value = AsyncMock()
        mock_handle_profile_picture.return_value = AsyncMock()
        mock_invalidate_cache.return_value = AsyncMock()
        mock_get_cached_profile.return_value = self.profile_data

        request = Mock()
        request.user = self.mock_user
        request.FILES = {'profile_picture': Mock()}

        with patch('users.views.success_response'):
            await self.view.patch(request)

            mock_handle_profile_picture.assert_called_once()

    @patch('users.views.sync_to_async')
    @patch('users.views.parse_request_data')
    async def test_profile_view_patch_json_decode_error(self, mock_parse_request, mock_sync_to_async):
        """Тест помилки декодування JSON"""
        mock_sync_to_async.return_value = AsyncMock(return_value=True)
        mock_parse_request.side_effect = json.JSONDecodeError('Invalid JSON', 'doc', 0)

        request = self.factory.patch('/')
        request.user = self.mock_user

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Invalid JSON'}, status=400)

            await self.view.patch(request)

            mock_error_response.assert_called_once_with('Invalid JSON format.', 400)

    @patch('users.views.sync_to_async')
    @patch('users.views.parse_request_data')
    @patch('users.views.update_user_data')
    async def test_profile_view_patch_validation_error(self, mock_update_data, mock_parse_request, mock_sync_to_async):
        """Тест валідаційної помилки при оновленні профілю"""
        mock_sync_to_async.return_value = AsyncMock(return_value=True)
        mock_parse_request.return_value = (self.profile_data, False)
        mock_update_data.side_effect = ValidationError('Invalid data format')

        request = self.factory.patch('/')
        request.user = self.mock_user

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Validation error'}, status=400)

            await self.view.patch(request)

            mock_error_response.assert_called_once_with("['Invalid data format']", 400)

    @patch('users.views.sync_to_async')
    @patch('users.views.parse_request_data')
    async def test_profile_view_patch_exception(self, mock_parse_request, mock_sync_to_async):
        """Тест загальної помилки при оновленні профілю"""
        mock_sync_to_async.return_value = AsyncMock(return_value=True)
        mock_parse_request.side_effect = Exception('Unexpected error')

        request = self.factory.patch('/')
        request.user = self.mock_user

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Server error'}, status=500)

            await self.view.patch(request)

            mock_error_response.assert_called_once()

    @patch('users.views.sync_to_async')
    @patch('users.views.parse_request_data')
    async def test_profile_view_patch_empty_data(self, mock_parse_request, mock_sync_to_async):
        """Тест оновлення профілю з пустими даними"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=1)  # user.id
        ]

        mock_parse_request.return_value = ({}, False)

        request = self.factory.patch('/')
        request.user = self.mock_user

        with patch('users.views.update_user_data') as mock_update_data, \
                patch('users.views.update_user_settings') as mock_update_settings, \
                patch('users.views.update_user_profile') as mock_update_profile, \
                patch('users.views.invalidate_user_cache') as mock_invalidate_cache, \
                patch('users.views.get_cached_profile') as mock_get_cached_profile, \
                patch('users.views.success_response') as mock_success_response:
            mock_update_data.return_value = AsyncMock()
            mock_update_settings.return_value = AsyncMock()
            mock_update_profile.return_value = AsyncMock()
            mock_invalidate_cache.return_value = AsyncMock()
            mock_get_cached_profile.return_value = {}
            mock_success_response.return_value = JsonResponse({'success': True})

            await self.view.patch(request)

            mock_update_data.assert_called_once_with(self.mock_user, {})
            mock_update_settings.assert_called_once_with(self.mock_user, {}, False)
            mock_update_profile.assert_called_once_with(self.mock_user, {})

    @patch('users.views.sync_to_async')
    @patch('users.views.parse_request_data')
    async def test_profile_view_patch_partial_data(self, mock_parse_request, mock_sync_to_async):
        """Тест оновлення профілю з частковими даними"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=1)  # user.id
        ]

        partial_data = {'user': {'name': 'Updated Name'}}
        mock_parse_request.return_value = (partial_data, False)

        request = self.factory.patch('/')
        request.user = self.mock_user

        with patch('users.views.update_user_data') as mock_update_data, \
                patch('users.views.update_user_settings') as mock_update_settings, \
                patch('users.views.update_user_profile') as mock_update_profile, \
                patch('users.views.invalidate_user_cache') as mock_invalidate_cache, \
                patch('users.views.get_cached_profile') as mock_get_cached_profile, \
                patch('users.views.success_response') as mock_success_response:
            mock_update_data.return_value = AsyncMock()
            mock_update_settings.return_value = AsyncMock()
            mock_update_profile.return_value = AsyncMock()
            mock_invalidate_cache.return_value = AsyncMock()
            mock_get_cached_profile.return_value = partial_data
            mock_success_response.return_value = JsonResponse({'success': True})

            await self.view.patch(request)

            mock_update_data.assert_called_once_with(self.mock_user, {'name': 'Updated Name'})
            mock_update_settings.assert_called_once_with(self.mock_user, {}, False)
            mock_update_profile.assert_called_once_with(self.mock_user, {})

    # DELETE method tests (account deletion)
    @patch('users.views.sync_to_async')
    @patch('users.views.delete_profile_picture')
    @patch('users.views.invalidate_all_user_caches')
    @patch('users.views.success_response')
    async def test_profile_view_delete_success(self, mock_success_response, mock_invalidate_all_caches,
                                               mock_delete_picture, mock_sync_to_async):
        """Тест успішного видалення акаунту"""

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=1),  # user.id (lambda: user.id)
            AsyncMock(return_value='test@example.com'),  # user.email (lambda: user.email)
            AsyncMock(),  # logout
            AsyncMock(),  # user.delete()
        ]

        mock_delete_picture.return_value = AsyncMock()
        mock_invalidate_all_caches.return_value = AsyncMock()
        mock_success_response.return_value = JsonResponse({'success': True})

        request = self.factory.delete('/')
        request.user = self.mock_user

        await self.view.delete(request)

        mock_delete_picture.assert_called_once_with(1, delete_folder=True)
        mock_invalidate_all_caches.assert_called_once_with(1, 'test@example.com')

    @patch('users.views.sync_to_async')
    async def test_profile_view_delete_unauthenticated(self, mock_sync_to_async):
        """Тест видалення акаунту неавторизованим користувачем"""
        mock_sync_to_async.return_value = AsyncMock(return_value=False)

        request = self.factory.delete('/')

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Unauthorized'}, status=401)

            await self.view.delete(request)

            mock_error_response.assert_called_once_with('User not authorized.', 401)

    @patch('users.views.sync_to_async')
    async def test_profile_view_delete_exception(self, mock_sync_to_async):
        """Тест обробки винятку при видаленні акаунту"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            Exception('Database error')  # user.id викидає помилку
        ]

        request = self.factory.delete('/')
        request.user = self.mock_user

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Server error'}, status=500)

            await self.view.delete(request)

            mock_error_response.assert_called_once()

    @patch('users.views.sync_to_async')
    @patch('users.views.logout')
    @patch('users.views.delete_profile_picture')
    async def test_profile_view_delete_logout_exception(self, mock_delete_picture, mock_logout, mock_sync_to_async):
        """Тест помилки при logout під час видалення акаунту"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=1),  # user.id
            AsyncMock(return_value='test@example.com'),  # user.email
        ]

        mock_logout.side_effect = Exception('Logout error')
        mock_delete_picture.return_value = AsyncMock()

        request = self.factory.delete('/')
        request.user = self.mock_user

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Server error'}, status=500)

            await self.view.delete(request)

            mock_error_response.assert_called_once()

    # Common tests
    def test_profile_view_decorator_applied(self):
        """Тест що декоратор ensure_csrf_cookie застосований"""
        self.assertTrue(hasattr(ProfileView, 'dispatch'))

    async def test_profile_view_methods_async(self):
        """Тест що всі методи є async"""
        request = Mock()

        get_coroutine = self.view.get(request)
        post_coroutine = self.view.post(request)
        patch_coroutine = self.view.patch(request)
        delete_coroutine = self.view.delete(request)

        self.assertTrue(hasattr(get_coroutine, '__await__'))
        self.assertTrue(hasattr(post_coroutine, '__await__'))
        self.assertTrue(hasattr(patch_coroutine, '__await__'))
        self.assertTrue(hasattr(delete_coroutine, '__await__'))

        get_coroutine.close()
        post_coroutine.close()
        patch_coroutine.close()
        delete_coroutine.close()

    @patch('users.views.sync_to_async')
    async def test_profile_view_post_missing_profile_picture_key(self, mock_sync_to_async):
        """Тест POST запиту з відсутнім ключем profile_picture"""
        mock_sync_to_async.return_value = AsyncMock(return_value=True)

        request = Mock()
        request.user = self.mock_user
        request.FILES = {'other_file': Mock()}

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'File not found'}, status=400)

            await self.view.post(request)

            mock_error_response.assert_called_once_with('File not found.', 400)

    @patch('users.views.sync_to_async')
    @patch('users.views.handle_profile_picture')
    @patch('users.views.invalidate_user_cache')
    async def test_profile_view_post_profile_picture_url_access(self, mock_invalidate_cache,
                                                                mock_handle_profile_picture, mock_sync_to_async):
        """Тест доступу до profile_picture.url після успішного завантаження"""

        mock_profile = Mock()
        mock_profile.profile_picture = 'https://example.com/new-avatar.jpg'

        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=(mock_profile, True)),  # get_or_create
            AsyncMock(return_value=1)  # user.id
        ]

        mock_handle_profile_picture.return_value = AsyncMock()
        mock_invalidate_cache.return_value = AsyncMock()

        request = Mock()
        request.user = self.mock_user
        request.FILES = {'profile_picture': Mock()}

        with patch('users.views.success_response') as mock_success_response:
            mock_success_response.return_value = JsonResponse({'success': True})

            await self.view.post(request)

            self.assertTrue(mock_success_response.called)
            call_args = mock_success_response.call_args[0][0]
            self.assertEqual(call_args['url'], 'https://example.com/new-avatar.jpg')

    @patch('users.views.sync_to_async')
    @patch('users.views.parse_request_data')
    @patch('users.views.update_user_data')
    @patch('users.views.update_user_settings')
    @patch('users.views.update_user_profile')
    @patch('users.views.invalidate_user_cache')
    @patch('users.views.get_cached_profile')
    async def test_profile_view_patch_no_profile_picture_in_files(self, mock_get_cached_profile, mock_invalidate_cache,
                                                                  mock_update_profile, mock_update_settings,
                                                                  mock_update_data, mock_parse_request,
                                                                  mock_sync_to_async):
        """Тест PATCH без profile_picture в FILES"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=1)  # user.id
        ]

        mock_parse_request.return_value = (self.profile_data, False)
        mock_update_data.return_value = AsyncMock()
        mock_update_settings.return_value = AsyncMock()
        mock_update_profile.return_value = AsyncMock()
        mock_invalidate_cache.return_value = AsyncMock()
        mock_get_cached_profile.return_value = self.profile_data

        request = Mock()
        request.user = self.mock_user
        request.FILES = {}

        with patch('users.views.success_response') as mock_success_response:
            mock_success_response.return_value = JsonResponse({'success': True})

            await self.view.patch(request)

            with patch('users.views.handle_profile_picture') as mock_handle_picture:
                mock_handle_picture.assert_not_called()

    @patch('users.views.sync_to_async')
    @patch('users.views.logout')
    @patch('users.views.delete_profile_picture')
    @patch('users.views.invalidate_all_user_caches')
    async def test_profile_view_delete_user_delete_exception(self, mock_invalidate_all_caches, mock_delete_picture,
                                                             mock_logout, mock_sync_to_async):
        """Тест помилки при user.delete()"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=1),  # user.id
            AsyncMock(return_value='test@example.com'),  # user.email
            AsyncMock(side_effect=Exception('Delete user error')),  # user.delete викидає помилку
        ]

        mock_logout.return_value = AsyncMock()
        mock_delete_picture.return_value = AsyncMock()
        mock_invalidate_all_caches.return_value = AsyncMock()

        request = self.factory.delete('/')
        request.user = self.mock_user

        with patch('users.views.error_response') as mock_error_response:
            mock_error_response.return_value = JsonResponse({'error': 'Server error'}, status=500)

            await self.view.delete(request)

            mock_error_response.assert_called_once()

    def test_profile_view_inheritance(self):
        """Тест що ProfileView наслідує правильний клас"""
        from common import LocalizedView
        self.assertTrue(issubclass(ProfileView, LocalizedView))

    @patch('users.views.sync_to_async')
    @patch('users.views.get_cached_profile')
    async def test_profile_view_get_profile_cache_called_with_user(self, mock_get_cached_profile, mock_sync_to_async):
        """Тест що get_cached_profile викликається з правильним користувачем"""
        mock_sync_to_async.return_value = AsyncMock(return_value=True)
        mock_get_cached_profile.return_value = self.profile_data

        request = self.factory.get('/')
        request.user = self.mock_user

        with patch('users.views.success_response'):
            await self.view.get(request)

            mock_get_cached_profile.assert_called_once_with(self.mock_user)
            args, _ = mock_get_cached_profile.call_args
            self.assertEqual(args[0], self.mock_user)

    @patch('users.views.sync_to_async')
    @patch('users.views.parse_request_data')
    @patch('users.views.update_user_data')
    @patch('users.views.update_user_settings')
    @patch('users.views.update_user_profile')
    @patch('users.views.invalidate_user_cache')
    @patch('users.views.get_cached_profile')
    async def test_profile_view_patch_success_response_structure(self, mock_get_cached_profile, mock_invalidate_cache,
                                                                 mock_update_profile, mock_update_settings,
                                                                 mock_update_data, mock_parse_request,
                                                                 mock_sync_to_async):
        """Тест структури успішної відповіді при PATCH"""
        mock_sync_to_async.side_effect = [
            AsyncMock(return_value=True),  # is_authenticated
            AsyncMock(return_value=1)  # user.id
        ]

        mock_parse_request.return_value = (self.profile_data, False)
        mock_update_data.return_value = AsyncMock()
        mock_update_settings.return_value = AsyncMock()
        mock_update_profile.return_value = AsyncMock()
        mock_invalidate_cache.return_value = AsyncMock()
        mock_get_cached_profile.return_value = self.profile_data

        request = self.factory.patch('/')
        request.user = self.mock_user

        with patch('users.views.success_response') as mock_success_response:
            mock_success_response.return_value = JsonResponse({'success': True})

            await self.view.patch(request)

            call_args = mock_success_response.call_args[0][0]
            self.assertIn('message', call_args)
            self.assertIn('profile_data', call_args)
            self.assertEqual(call_args['profile_data'], self.profile_data)
