from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from users.services.profile_picture_service import handle_profile_picture, delete_profile_picture
from users.models import UserProfile
from unittest.mock import patch, MagicMock
import asyncio

User = get_user_model()

class SupabaseIntegrationTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='Test',
            surname='User',
            email='supabase@example.com',
            password='TestPass123!',
            role='student',
            is_verified_email=True,
            is_active=True
        )
        self.user_profile, _ = UserProfile.objects.get_or_create(user=self.user)

    @patch('users.services.profile_picture_service.supabase')
    def test_profile_picture_upload_integration(self, mock_supabase):
        """Інтеграція завантаження зображення профілю"""
        mock_bucket = MagicMock()
        mock_bucket.upload.return_value = {'error': None}
        # Виправляємо формат відповіді - повертаємо тільки URL
        mock_bucket.get_public_url.return_value = 'https://storage.example.com/avatar.jpg'

        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket
        mock_supabase.storage = mock_storage

        async def test_flow():
            test_image = SimpleUploadedFile(
                "test.jpg",
                b"fake image content",
                content_type="image/jpeg"
            )

            await handle_profile_picture(self.user_profile, test_image)

            await self.user_profile.arefresh_from_db()
            self.assertEqual(self.user_profile.profile_picture, 'https://storage.example.com/avatar.jpg')

        asyncio.run(test_flow())

    @patch('users.services.profile_picture_service.supabase')
    def test_profile_picture_deletion_integration(self, mock_supabase):
        """Інтеграція видалення зображення профілю"""
        mock_bucket = MagicMock()
        # Виправляємо формат відповіді для list - повертаємо список файлів безпосередньо
        mock_bucket.list.return_value = [{'name': 'avatar.jpg'}]
        mock_bucket.remove.return_value = {'error': None}

        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket
        mock_supabase.storage = mock_storage

        async def test_flow():
            await delete_profile_picture(self.user.id, delete_folder=True)

            mock_bucket.list.assert_called()
            mock_bucket.remove.assert_called()

        asyncio.run(test_flow())

    @patch('users.services.profile_picture_service.supabase')
    def test_file_validation_integration(self, mock_supabase):
        """Тест валідації файлів"""
        mock_bucket = MagicMock()
        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket
        mock_supabase.storage = mock_storage

        async def test_flow():
            # Невалідний тип файлу
            invalid_file = SimpleUploadedFile(
                "test.txt",
                b"text content",
                content_type="text/plain"
            )

            with self.assertRaises(Exception):
                await handle_profile_picture(self.user_profile, invalid_file)

            # Занадто великий файл
            large_file = SimpleUploadedFile(
                "large.jpg",
                b"x" * (6 * 1024 * 1024),  # 6MB
                content_type="image/jpeg"
            )

            with self.assertRaises(Exception):
                await handle_profile_picture(self.user_profile, large_file)

        asyncio.run(test_flow())

    @patch('users.services.profile_picture_service.supabase')
    def test_upload_error_handling(self, mock_supabase):
        """Тест обробки помилок при завантаженні"""
        mock_bucket = MagicMock()
        mock_bucket.upload.return_value = {'error': {'message': 'Upload failed'}}

        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket
        mock_supabase.storage = mock_storage

        async def test_flow():
            test_image = SimpleUploadedFile(
                "test.jpg",
                b"fake image content",
                content_type="image/jpeg"
            )

            with self.assertRaises(Exception):
                await handle_profile_picture(self.user_profile, test_image)

        asyncio.run(test_flow())

    @patch('users.services.profile_picture_service.supabase')
    def test_deletion_error_handling(self, mock_supabase):
        """Тест обробки помилок при видаленні"""
        mock_bucket = MagicMock()
        mock_bucket.list.return_value = [{'name': 'avatar.jpg'}]
        # Додаємо помилку для list операції замість remove
        mock_bucket.list.return_value = {'error': {'message': 'List failed'}, 'data': None}
        mock_bucket.remove.return_value = {'error': None}

        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket
        mock_supabase.storage = mock_storage

        async def test_flow():
            with self.assertRaises(Exception):
                await delete_profile_picture(self.user.id, delete_folder=True)

        asyncio.run(test_flow())

    @patch('users.services.profile_picture_service.supabase')
    def test_deletion_list_error_handling(self, mock_supabase):
        """Тест обробки помилок при отриманні списку файлів"""
        mock_bucket = MagicMock()
        # Моделюємо помилку при отриманні списку файлів
        mock_bucket.list.side_effect = Exception("Supabase connection error")

        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket
        mock_supabase.storage = mock_storage

        async def test_flow():
            with self.assertRaises(Exception):
                await delete_profile_picture(self.user.id, delete_folder=True)

        asyncio.run(test_flow())
