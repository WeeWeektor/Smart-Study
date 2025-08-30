import asyncio
from unittest.mock import patch, Mock, AsyncMock
from django.test import TestCase
from django.core.exceptions import ValidationError
from users.services import profile_picture_service


class TestProfilePictureService(TestCase):
    def setUp(self):
        self.user = Mock()
        self.user.id = 1

        self.user_profile = Mock()
        self.user_profile.user = self.user
        self.user_profile.profile_picture = None
        self.user_profile.save = Mock()

        self.profile_picture = Mock()
        self.profile_picture.content_type = 'image/jpeg'
        self.profile_picture.size = 1024 * 1024
        self.profile_picture.name = 'test.jpg'
        self.profile_picture.read = Mock(return_value=b'fake_image_data')

    def test_handle_profile_picture_unsupported_file_type(self):
        self.profile_picture.content_type = 'application/pdf'

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(profile_picture_service.handle_profile_picture(
                self.user_profile, self.profile_picture
            ))

        self.assertIn("Unsupported file type", str(cm.exception))

    def test_handle_profile_picture_file_too_large(self):
        self.profile_picture.size = 6 * 1024 * 1024

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(profile_picture_service.handle_profile_picture(
                self.user_profile, self.profile_picture
            ))

        self.assertIn("Too much file size", str(cm.exception))

    @patch('users.services.profile_picture_service.sync_to_async')
    @patch('users.services.profile_picture_service.supabase')
    @patch('users.services.profile_picture_service.uuid.uuid4')
    @patch('users.services.profile_picture_service.time.time')
    def test_handle_profile_picture_success_no_existing_picture(
            self, mock_time, mock_uuid, mock_supabase, mock_sync_to_async
    ):
        mock_uuid.return_value = Mock()
        mock_uuid.return_value.__str__ = Mock(return_value='test-uuid')
        mock_time.return_value = 1234567890

        mock_bucket = Mock()
        mock_supabase.storage.from_.return_value = mock_bucket
        mock_bucket.upload = Mock()
        mock_bucket.get_public_url = Mock(return_value='https://example.com/image.jpg')

        mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func()) if callable(func) else AsyncMock(
            return_value=func)

        asyncio.run(profile_picture_service.handle_profile_picture(
            self.user_profile, self.profile_picture
        ))

        mock_supabase.storage.from_.assert_called_once()
        self.assertEqual(self.user_profile.profile_picture, 'https://example.com/image.jpg')

    @patch('users.services.profile_picture_service.sync_to_async')
    @patch('users.services.profile_picture_service.supabase')
    @patch('users.services.profile_picture_service.delete_profile_picture', new_callable=AsyncMock)
    @patch('users.services.profile_picture_service.uuid.uuid4')
    @patch('users.services.profile_picture_service.time.time')
    def test_handle_profile_picture_success_with_existing_picture(
            self, mock_time, mock_uuid, mock_delete, mock_supabase, mock_sync_to_async
    ):
        self.user_profile.profile_picture = 'https://example.com/old_image.jpg'

        mock_uuid.return_value = Mock()
        mock_uuid.return_value.__str__ = Mock(return_value='test-uuid')
        mock_time.return_value = 1234567890

        mock_bucket = Mock()
        mock_supabase.storage.from_.return_value = mock_bucket
        mock_bucket.upload = Mock()
        mock_bucket.get_public_url = Mock(return_value='https://example.com/new_image.jpg')

        mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func()) if callable(func) else AsyncMock(
            return_value=func)

        asyncio.run(profile_picture_service.handle_profile_picture(
            self.user_profile, self.profile_picture
        ))

        mock_delete.assert_called_once_with(1, delete_folder=False)
        self.assertEqual(self.user_profile.profile_picture, 'https://example.com/new_image.jpg')

    @patch('users.services.profile_picture_service.sync_to_async')
    @patch('users.services.profile_picture_service.supabase')
    @patch('users.services.profile_picture_service.delete_profile_picture', new_callable=AsyncMock)
    @patch('users.services.profile_picture_service.logging.getLogger')
    @patch('users.services.profile_picture_service.uuid.uuid4')
    @patch('users.services.profile_picture_service.time.time')
    def test_handle_profile_picture_delete_old_picture_fails(
            self, mock_time, mock_uuid, mock_logger, mock_delete, mock_supabase, mock_sync_to_async
    ):
        self.user_profile.profile_picture = 'https://example.com/old_image.jpg'
        mock_delete.side_effect = FileNotFoundError("File not found")

        mock_uuid.return_value = Mock()
        mock_uuid.return_value.__str__ = Mock(return_value='test-uuid')
        mock_time.return_value = 1234567890

        mock_bucket = Mock()
        mock_supabase.storage.from_.return_value = mock_bucket
        mock_bucket.upload = Mock()
        mock_bucket.get_public_url = Mock(return_value='https://example.com/new_image.jpg')

        mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func()) if callable(func) else AsyncMock(
            return_value=func)

        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        asyncio.run(profile_picture_service.handle_profile_picture(
            self.user_profile, self.profile_picture
        ))

        mock_logger_instance.warning.assert_called_once()
        self.assertEqual(self.user_profile.profile_picture, 'https://example.com/new_image.jpg')

    @patch('users.services.profile_picture_service.sync_to_async')
    @patch('users.services.profile_picture_service.supabase')
    @patch('users.services.profile_picture_service.uuid.uuid4')
    @patch('users.services.profile_picture_service.time.time')
    def test_handle_profile_picture_upload_fails(
            self, mock_time, mock_uuid, mock_supabase, mock_sync_to_async
    ):
        mock_uuid.return_value = Mock()
        mock_uuid.return_value.__str__ = Mock(return_value='test-uuid')
        mock_time.return_value = 1234567890

        mock_bucket = Mock()
        mock_supabase.storage.from_.return_value = mock_bucket

        call_count = 0

        def sync_to_async_side_effect(func):
            nonlocal call_count
            call_count += 1

            if call_count <= 2:
                if call_count == 1:
                    return AsyncMock(return_value=1)
                else:
                    return AsyncMock(return_value=b'fake_image_data')
            elif call_count == 3:
                return AsyncMock(side_effect=Exception("Upload failed"))
            else:
                return AsyncMock()

        mock_sync_to_async.side_effect = sync_to_async_side_effect

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(profile_picture_service.handle_profile_picture(
                self.user_profile, self.profile_picture
            ))

        self.assertIn("Error when uploading a file to Supabase", str(cm.exception))

    @patch('users.services.profile_picture_service.sync_to_async')
    @patch('users.services.profile_picture_service.supabase')
    def test_delete_profile_picture_success(self, mock_supabase, mock_sync_to_async):
        mock_bucket = Mock()
        mock_supabase.storage.from_.return_value = mock_bucket

        mock_files = [
            {'name': 'image1.jpg'},
            {'name': 'image2.png'}
        ]

        def sync_to_async_side_effect(func):
            if hasattr(func, '__name__') and 'list' in str(func):
                return AsyncMock(return_value=mock_files)
            return AsyncMock()

        mock_sync_to_async.side_effect = sync_to_async_side_effect

        asyncio.run(profile_picture_service.delete_profile_picture(1, delete_folder=False))

        mock_supabase.storage.from_.assert_called_once()

    @patch('users.services.profile_picture_service.sync_to_async')
    @patch('users.services.profile_picture_service.supabase')
    def test_delete_profile_picture_with_folder_deletion(self, mock_supabase, mock_sync_to_async):
        mock_bucket = Mock()
        mock_supabase.storage.from_.return_value = mock_bucket

        mock_files = [{'name': 'image1.jpg'}]

        def sync_to_async_side_effect(func):
            if hasattr(func, '__name__') and 'list' in str(func):
                return AsyncMock(return_value=mock_files)
            return AsyncMock()

        mock_sync_to_async.side_effect = sync_to_async_side_effect

        asyncio.run(profile_picture_service.delete_profile_picture(1, delete_folder=True))

        mock_supabase.storage.from_.assert_called_once()

    @patch('users.services.profile_picture_service.sync_to_async')
    @patch('users.services.profile_picture_service.supabase')
    def test_delete_profile_picture_no_files(self, mock_supabase, mock_sync_to_async):
        mock_bucket = Mock()
        mock_supabase.storage.from_.return_value = mock_bucket

        def sync_to_async_side_effect(func):
            if hasattr(func, '__name__') and 'list' in str(func):
                return AsyncMock(return_value=[])
            return AsyncMock()

        mock_sync_to_async.side_effect = sync_to_async_side_effect

        asyncio.run(profile_picture_service.delete_profile_picture(1, delete_folder=False))

        mock_supabase.storage.from_.assert_called_once()

    @patch('users.services.profile_picture_service.sync_to_async')
    @patch('users.services.profile_picture_service.supabase')
    @patch('users.services.profile_picture_service.logging.getLogger')
    def test_delete_profile_picture_exception(self, mock_logger, mock_supabase, mock_sync_to_async):
        mock_bucket = Mock()
        mock_supabase.storage.from_.return_value = mock_bucket

        mock_sync_to_async.side_effect = Exception("Supabase error")

        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(profile_picture_service.delete_profile_picture(1, delete_folder=False))

        mock_logger_instance.error.assert_called_once()
        self.assertIn("Unable to delete profile photo", str(cm.exception))

    def test_handle_profile_picture_different_file_extensions(self):
        test_cases = [
            ('image/png', 'test.PNG', 'png'),
            ('image/gif', 'test.GIF', 'gif'),
            ('image/webp', 'test.WEBP', 'webp')
        ]

        for content_type, filename, expected_ext in test_cases:
            with self.subTest(content_type=content_type):
                self.profile_picture.content_type = content_type
                self.profile_picture.name = filename

                try:
                    with patch('users.services.profile_picture_service.sync_to_async'), \
                            patch('users.services.profile_picture_service.supabase'), \
                            patch('users.services.profile_picture_service.uuid.uuid4'), \
                            patch('users.services.profile_picture_service.time.time'):
                        asyncio.run(profile_picture_service.handle_profile_picture(
                            self.user_profile, self.profile_picture
                        ))
                except ValidationError as e:
                    if "Unsupported file type" in str(e):
                        self.fail(f"Valid file type {content_type} was rejected")
                except:
                    pass
