import io

from PIL import Image
from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
import json

from django.urls import reverse

User = get_user_model()

class FileUploadE2ETest(TransactionTestCase):
    """End-to-end тести для завантаження файлів"""

    def setUp(self):
        self.client = Client()
        cache.clear()
        self.user = User.objects.create_user(
            email='filetest@example.com',
            password='FileTest123!',
            is_verified_email=True,
            is_active=True
        )
        self.client.force_login(self.user)

    def create_test_image(self, format='JPEG', size=(100, 100)):
        """Створює реальне зображення для тестування"""
        image = Image.new('RGB', size, color='red')
        image_file = io.BytesIO()
        image.save(image_file, format=format)
        image_file.seek(0)
        image_file.name = f'test.{format.lower()}'
        return image_file

    def test_avatar_upload_complete_workflow(self):
        """Тест повного робочого процесу завантаження аватара"""

        test_image = self.create_test_image('JPEG')
        test_image.content_type = 'image/jpeg'

        response = self.client.post(
            reverse('user_urls:profile'),
            {'profile_picture': test_image},
            format='multipart'
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/user/profile/')
        data = response.json()
        first_avatar = data.get('profile', {}).get('profile_picture')
        self.assertIsNotNone(first_avatar)

        new_image = SimpleUploadedFile(
            "new_avatar.png",
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x02\x00\x00\x00\x02\x08\x02\x00\x00\x00\x90wS\xde",
            content_type="image/png"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': new_image}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/user/profile/')
        data = response.json()
        second_avatar = data.get('profile', {}).get('profile_picture')
        self.assertIsNotNone(second_avatar)
        self.assertNotEqual(first_avatar, second_avatar)

        response = self.client.patch(
            '/api/user/profile/',
            data=json.dumps({
                'profile': {
                    'profile_picture': None
                }
            }),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [200, 204])

        response = self.client.get('/api/user/profile/')
        data = response.json()
        profile_picture = data.get('profile', {}).get('profile_picture')

        self.assertIsNotNone(data.get('profile'))

        final_image = SimpleUploadedFile(
            "final_avatar.jpg",
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C',
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': final_image}
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_file_upload_handling(self):
        """Обробка завантаження невалідних файлів"""
        invalid_file = SimpleUploadedFile(
            "malicious.exe",
            b"fake executable content",
            content_type="application/x-executable"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': invalid_file}
        )
        self.assertEqual(response.status_code, 400)

        large_file = SimpleUploadedFile(
            "large.jpg",
            b"x" * (10 * 1024 * 1024),
            content_type="image/jpeg"
        )

        response = self.client.post(
            '/api/user/profile/',
            {'profile_picture': large_file}
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/api/user/profile/')
        self.assertEqual(response.status_code, 200)
