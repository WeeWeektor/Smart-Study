from unittest.mock import Mock, patch
from django.core.exceptions import ValidationError
from django.test import TestCase
from common.services import validate_picture_file_security, MAX_FILE_SIZE


class TestFileValidationService(TestCase):

    @staticmethod
    def create_mock_file(content, filename, content_type, size=None):
        """Створює mock файл для тестів"""
        mock_file = Mock()
        mock_file.read.return_value = content
        mock_file.seek = Mock()
        mock_file.name = filename
        mock_file.content_type = content_type
        mock_file.size = size or len(content)
        return mock_file

    def test_valid_jpeg_file(self):
        """Тест валідного JPEG файлу"""
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF'
        mock_file = self.create_mock_file(
            content=jpeg_header + b'\x00' * 100,
            filename='test.jpg',
            content_type='image/jpeg'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', return_value='image/jpeg'):
            result = validate_picture_file_security(mock_file)
            self.assertTrue(result)

    def test_valid_png_file(self):
        """Тест валідного PNG файлу"""
        png_header = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
        mock_file = self.create_mock_file(
            content=png_header + b'\x00' * 100,
            filename='test.png',
            content_type='image/png'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', return_value='image/png'):
            result = validate_picture_file_security(mock_file)
            self.assertTrue(result)

    def test_valid_gif_file(self):
        """Тест валідного GIF файлу"""
        gif_header = b'\x47\x49\x46\x38\x39\x61'
        mock_file = self.create_mock_file(
            content=gif_header + b'\x00' * 100,
            filename='test.gif',
            content_type='image/gif'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', return_value='image/gif'):
            result = validate_picture_file_security(mock_file)
            self.assertTrue(result)

    def test_valid_webp_file(self):
        """Тест валідного WebP файлу"""
        webp_header = b'\x52\x49\x46\x46' + b'\x00' * 4 + b'\x57\x45\x42\x50'
        mock_file = self.create_mock_file(
            content=webp_header + b'\x00' * 100,
            filename='test.webp',
            content_type='image/webp'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', return_value='image/webp'):
            result = validate_picture_file_security(mock_file)
            self.assertTrue(result)

    def test_file_too_large(self):
        """Тест файлу, що перевищує максимальний розмір"""
        mock_file = self.create_mock_file(
            content=b'\xff\xd8\xff\xe0',
            filename='large.jpg',
            content_type='image/jpeg',
            size=MAX_FILE_SIZE + 1
        )

        with self.assertRaises(ValidationError) as context:
            validate_picture_file_security(mock_file)

        self.assertIn('File too large', str(context.exception))

    def test_disallowed_file_type(self):
        """Тест недозволеного типу файлу"""
        mock_file = self.create_mock_file(
            content=b'test content',
            filename='test.txt',
            content_type='text/plain'
        )

        with self.assertRaises(ValidationError) as context:
            validate_picture_file_security(mock_file)

        self.assertIn('File type not allowed', str(context.exception))

    def test_invalid_file_signature(self):
        """Тест файлу з невідповідною сигнатурою"""
        mock_file = self.create_mock_file(
            content=b'invalid signature',
            filename='test.jpg',
            content_type='image/jpeg'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', return_value='image/jpeg'):
            with self.assertRaises(ValidationError) as context:
                validate_picture_file_security(mock_file)

            self.assertIn('File signature does not match', str(context.exception))

    def test_content_type_spoofing(self):
        """Тест підміни Content-Type"""
        jpeg_header = b'\xff\xd8\xff\xe0'
        mock_file = self.create_mock_file(
            content=jpeg_header + b'\x00' * 100,
            filename='test.jpg',
            content_type='image/jpeg'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', return_value='image/png'):
            with self.assertRaises(ValidationError) as context:
                validate_picture_file_security(mock_file)

            self.assertIn('Content-Type spoofing detected', str(context.exception))

    def test_dangerous_php_extension(self):
        """Тест небезпечного розширення .php"""
        jpeg_header = b'\xff\xd8\xff\xe0'
        mock_file = self.create_mock_file(
            content=jpeg_header + b'\x00' * 100,
            filename='malicious.php.jpg',
            content_type='image/jpeg'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', return_value='image/jpeg'):
            with self.assertRaises(ValidationError) as context:
                validate_picture_file_security(mock_file)

            self.assertIn('Dangerous file extension detected', str(context.exception))

    def test_dangerous_exe_extension(self):
        """Тест небезпечного розширення .exe"""
        jpeg_header = b'\xff\xd8\xff\xe0'
        mock_file = self.create_mock_file(
            content=jpeg_header + b'\x00' * 100,
            filename='virus.exe.jpg',
            content_type='image/jpeg'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', return_value='image/jpeg'):
            with self.assertRaises(ValidationError) as context:
                validate_picture_file_security(mock_file)

            self.assertIn('Dangerous file extension detected', str(context.exception))

    def test_magic_library_exception(self):
        """Тест обробки винятку від magic бібліотеки"""
        jpeg_header = b'\xff\xd8\xff\xe0'
        mock_file = self.create_mock_file(
            content=jpeg_header + b'\x00' * 100,
            filename='test.jpg',
            content_type='image/jpeg'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', side_effect=Exception('Magic error')):
            result = validate_picture_file_security(mock_file)
            self.assertTrue(result)

    def test_file_seek_called(self):
        """Тест що метод seek викликається правильно"""
        jpeg_header = b'\xff\xd8\xff\xe0'
        mock_file = self.create_mock_file(
            content=jpeg_header + b'\x00' * 100,
            filename='test.jpg',
            content_type='image/jpeg'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', return_value='image/jpeg'):
            validate_picture_file_security(mock_file)

            self.assertEqual(mock_file.seek.call_count, 2)
            mock_file.seek.assert_called_with(0)

    def test_gif87a_variant(self):
        """Тест GIF87a варіанту"""
        gif_header = b'\x47\x49\x46\x38\x37\x61'
        mock_file = self.create_mock_file(
            content=gif_header + b'\x00' * 100,
            filename='test.gif',
            content_type='image/gif'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', return_value='image/gif'):
            result = validate_picture_file_security(mock_file)
            self.assertTrue(result)

    def test_case_insensitive_dangerous_extensions(self):
        """Тест регістронезалежного виявлення небезпечних розширень"""
        jpeg_header = b'\xff\xd8\xff\xe0'
        mock_file = self.create_mock_file(
            content=jpeg_header + b'\x00' * 100,
            filename='TEST.PHP.JPG',
            content_type='image/jpeg'
        )

        with patch('common.services.picture_validation_service.magic.from_buffer', return_value='image/jpeg'):
            with self.assertRaises(ValidationError) as context:
                validate_picture_file_security(mock_file)

            self.assertIn('Dangerous file extension detected', str(context.exception))
