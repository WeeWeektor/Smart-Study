import asyncio
from unittest.mock import patch, MagicMock

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from users.models import CustomUser, UserProfile
from users.services.profile_picture_service import handle_profile_picture, delete_profile_picture


class TestProfilePictureService(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            name="Test",
            surname="User",
            email="test@example.com",
            password="testpass123",
            role="student"
        )
        self.user_profile = UserProfile.objects.create(user=self.user)

    def create_valid_jpeg_file(self, filename="test.jpg", size_kb=100):
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C'
        content = jpeg_header + b'\x00' * (size_kb * 1024 - len(jpeg_header))
        return SimpleUploadedFile(filename, content, content_type="image/jpeg")

    def create_valid_png_file(self, filename="test.png", size_kb=100):
        png_header = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0dIHDR'
        content = png_header + b'\x00' * (size_kb * 1024 - len(png_header))
        return SimpleUploadedFile(filename, content, content_type="image/png")

    def test_handle_profile_picture_unsupported_file_type(self):
        invalid_file = SimpleUploadedFile("test.txt", b"This is a text file", content_type="text/plain")

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(handle_profile_picture(self.user_profile, invalid_file))
        self.assertIn("File type not allowed", str(cm.exception))

    def test_handle_profile_picture_file_too_large(self):
        large_file = SimpleUploadedFile(
            "large.jpg",
            b'\xff\xd8\xff\xe0' + b'\x00' * (6 * 1024 * 1024),
            content_type="image/jpeg"
        )

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(handle_profile_picture(self.user_profile, large_file))
        self.assertIn("File too large", str(cm.exception))

    @patch('users.services.profile_picture_service.supabase')
    @patch('common.services.picture_validation_service.magic.from_buffer')
    async def test_handle_profile_picture_success_no_existing_picture(self, mock_magic, mock_supabase):
        mock_magic.return_value = "image/jpeg"

        mock_bucket = MagicMock()
        mock_bucket.upload = MagicMock(return_value=None)
        mock_bucket.get_public_url = MagicMock(return_value="https://example.com/image.jpg")
        mock_supabase.storage.from_.return_value = mock_bucket

        valid_jpeg = self.create_valid_jpeg_file()

        await handle_profile_picture(self.user_profile, valid_jpeg)

        await sync_to_async(self.user_profile.refresh_from_db)()
        self.assertEqual(self.user_profile.profile_picture, "https://example.com/image.jpg")

    @patch('users.services.profile_picture_service.delete_profile_picture')
    @patch('users.services.profile_picture_service.supabase')
    @patch('common.services.picture_validation_service.magic.from_buffer')
    async def test_handle_profile_picture_success_with_existing_picture(self, mock_magic, mock_supabase, mock_delete):
        mock_magic.return_value = "image/jpeg"

        async def mock_delete_coroutine(*args, **kwargs):
            return None

        mock_delete.return_value = mock_delete_coroutine()

        self.user_profile.profile_picture = "https://example.com/old-image.jpg"
        await sync_to_async(self.user_profile.save)()

        mock_bucket = MagicMock()
        mock_bucket.upload = MagicMock(return_value=None)
        mock_bucket.get_public_url = MagicMock(return_value="https://example.com/new-image.jpg")
        mock_supabase.storage.from_.return_value = mock_bucket

        valid_jpeg = self.create_valid_jpeg_file()

        await handle_profile_picture(self.user_profile, valid_jpeg)

        await sync_to_async(self.user_profile.refresh_from_db)()
        self.assertEqual(self.user_profile.profile_picture, "https://example.com/new-image.jpg")

    @patch('users.services.profile_picture_service.delete_profile_picture')
    @patch('users.services.profile_picture_service.supabase')
    @patch('common.services.picture_validation_service.magic.from_buffer')
    async def test_handle_profile_picture_delete_old_picture_fails(self, mock_magic, mock_supabase, mock_delete):
        mock_magic.return_value = "image/jpeg"
        mock_delete.side_effect = Exception("Delete failed")

        self.user_profile.profile_picture = "https://example.com/old-image.jpg"
        await sync_to_async(self.user_profile.save)()

        mock_bucket = MagicMock()
        mock_bucket.upload = MagicMock(return_value=None)
        mock_bucket.get_public_url = MagicMock(return_value="https://example.com/new-image.jpg")
        mock_supabase.storage.from_.return_value = mock_bucket

        valid_jpeg = self.create_valid_jpeg_file()

        await handle_profile_picture(self.user_profile, valid_jpeg)

        await sync_to_async(self.user_profile.refresh_from_db)()
        self.assertEqual(self.user_profile.profile_picture, "https://example.com/new-image.jpg")

    def test_handle_profile_picture_invalid_file_signature(self):
        invalid_file = SimpleUploadedFile("fake.jpg", b"This is not a real JPEG file", content_type="image/jpeg")

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(handle_profile_picture(self.user_profile, invalid_file))
        self.assertIn("File signature does not match", str(cm.exception))

    def test_handle_profile_picture_dangerous_extension(self):
        dangerous_file = SimpleUploadedFile(
            "script.jpg.exe",
            b'\xff\xd8\xff\xe0' + b'\x00' * 100,
            content_type="image/jpeg"
        )

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(handle_profile_picture(self.user_profile, dangerous_file))
        self.assertIn("Dangerous file extension", str(cm.exception))

    @patch('users.services.profile_picture_service.supabase')
    @patch('common.services.picture_validation_service.magic.from_buffer')
    def test_handle_profile_picture_upload_fails(self, mock_magic, mock_supabase):
        mock_magic.return_value = "image/jpeg"

        mock_bucket = MagicMock()
        mock_bucket.upload = MagicMock(side_effect=Exception("Upload failed"))
        mock_supabase.storage.from_.return_value = mock_bucket

        valid_jpeg = self.create_valid_jpeg_file()

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(handle_profile_picture(self.user_profile, valid_jpeg))
        self.assertIn("Failed to upload file", str(cm.exception))

    @patch('common.services.picture_validation_service.magic.from_buffer')
    def test_handle_profile_picture_content_type_spoofing(self, mock_magic):
        mock_magic.return_value = "image/png"
        spoofed_file = self.create_valid_jpeg_file("test.jpg")

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(handle_profile_picture(self.user_profile, spoofed_file))
        self.assertIn("Content-Type spoofing detected", str(cm.exception))

    @patch('users.services.profile_picture_service.supabase')
    def test_delete_profile_picture_success(self, mock_supabase):
        mock_bucket = MagicMock()
        mock_bucket.list = MagicMock(return_value=[{'name': 'image.jpg'}])
        mock_bucket.remove = MagicMock(return_value=None)
        mock_supabase.storage.from_.return_value = mock_bucket

        asyncio.run(delete_profile_picture(self.user.id))

        mock_bucket.list.assert_called_once()
        mock_bucket.remove.assert_called_once()

    @patch('users.services.profile_picture_service.supabase')
    def test_delete_profile_picture_with_folder(self, mock_supabase):
        mock_bucket = MagicMock()
        mock_bucket.list = MagicMock(return_value=[{'name': 'image.jpg'}])
        mock_bucket.remove = MagicMock(return_value=None)
        mock_supabase.storage.from_.return_value = mock_bucket

        asyncio.run(delete_profile_picture(self.user.id, delete_folder=True))

        self.assertEqual(mock_bucket.remove.call_count, 2)

    @patch('users.services.profile_picture_service.supabase')
    def test_delete_profile_picture_fails(self, mock_supabase):
        mock_bucket = MagicMock()
        mock_bucket.list = MagicMock(side_effect=Exception("Delete failed"))
        mock_supabase.storage.from_.return_value = mock_bucket

        with self.assertRaises(ValidationError) as cm:
            asyncio.run(delete_profile_picture(self.user.id))
        self.assertIn("Unable to delete profile photo", str(cm.exception))
