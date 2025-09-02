import asyncio
from unittest.mock import patch

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase

from users.utils.validators import (
    email_validator,
    phone_validator,
    cached_email_validator
)


class TestValidators(TestCase):
    def setUp(self):
        """Очищення кешу перед кожним тестом"""
        cache.clear()

    def tearDown(self):
        """Очищення кешу після кожного тесту"""
        cache.clear()

    def test_email_validator_valid_emails(self):
        """Тест валідних email адрес"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.org',
            'user+tag@example.co.uk',
            'test123@gmail.com',
            'simple@test.io'
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                try:
                    email_validator(email)
                except ValidationError:
                    self.fail(f'ValidationError raised for valid email: {email}')

    def test_email_validator_invalid_emails(self):
        """Тест невалідних email адрес"""
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'user@',
            'user space@domain.com',
            'user@domain',
            '',
            'user@@domain.com'
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                with self.assertRaises(ValidationError):
                    email_validator(email)

    def test_email_validator_error_message(self):
        """Тест повідомлення про помилку email валідатора"""
        with self.assertRaises(ValidationError) as context:
            email_validator('invalid-email')

        self.assertIn('Incorrect email format.', str(context.exception))

    def test_phone_validator_valid_phones(self):
        """Тест валідних номерів телефонів"""
        valid_phones = [
            '+1234567890',
            '1234567890',
            '+380123456789',
            '380123456789',
            '+12345678901234',
            '123456789012345'
        ]

        for phone in valid_phones:
            with self.subTest(phone=phone):
                try:
                    phone_validator(phone)
                except ValidationError:
                    self.fail(f'ValidationError raised for valid phone: {phone}')

    def test_phone_validator_invalid_phones(self):
        """Тест невалідних номерів телефонів"""
        invalid_phones = [
            '123456789',
            '1234567890123456',
            '+12345abc90',
            '+12 34 567 890',
            '+12-34-567-890',
            '',
            'abc',
            '+',
            '++1234567890'
        ]

        for phone in invalid_phones:
            with self.subTest(phone=phone):
                with self.assertRaises(ValidationError):
                    phone_validator(phone)

    def test_phone_validator_error_message(self):
        """Тест повідомлення про помилку phone валідатора"""
        with self.assertRaises(ValidationError) as context:
            phone_validator('123')

        self.assertIn('The phone number must contain between 10 and 15 digits', str(context.exception))

    async def test_cached_email_validator_valid_email_not_cached(self):
        """Тест валідного email без кешу"""
        email = 'test@example.com'
        cache_key = f"email_valid_{hash(email)}"

        self.assertIsNone(cache.get(cache_key))

        result = await cached_email_validator(email)

        self.assertTrue(result)
        self.assertTrue(cache.get(cache_key))

    async def test_cached_email_validator_valid_email_cached(self):
        """Тест валідного email з кешем"""
        email = 'test@example.com'
        cache_key = f"email_valid_{hash(email)}"

        cache.set(cache_key, True, timeout=30 * 60)

        with patch('users.utils.validators.email_validator') as mock_validator:
            result = await cached_email_validator(email)

            self.assertTrue(result)
            mock_validator.assert_not_called()

    async def test_cached_email_validator_invalid_email_not_cached(self):
        """Тест невалідного email без кешу"""
        email = 'invalid-email'
        cache_key = f"email_valid_{hash(email)}"

        self.assertIsNone(cache.get(cache_key))

        with self.assertRaises(ValidationError):
            await cached_email_validator(email)

        self.assertFalse(cache.get(cache_key))

    async def test_cached_email_validator_invalid_email_cached(self):
        """Тест невалідного email з кешем"""
        email = 'invalid-email'
        cache_key = f"email_valid_{hash(email)}"

        cache.set(cache_key, False, timeout=30 * 60)

        with patch('users.utils.validators.email_validator') as mock_validator:
            with self.assertRaises(ValidationError):
                await cached_email_validator(email)

            mock_validator.assert_not_called()

    @patch('users.utils.validators.gettext')
    async def test_cached_email_validator_error_message(self, mock_gettext):
        """Тест повідомлення про помилку в cached_email_validator"""
        mock_gettext.return_value = 'Incorrect email format.'

        with self.assertRaises(ValidationError) as context:
            await cached_email_validator('invalid-email')

        mock_gettext.assert_called_with('Incorrect email format.')
        self.assertIn('Incorrect email format.', str(context.exception))

    async def test_cached_email_validator_cache_timeout(self):
        """Тест таймауту кешу"""
        email = 'test@example.com'
        cache_key = f"email_valid_{hash(email)}"

        with patch('users.utils.validators.cache.set') as mock_cache_set:
            await cached_email_validator(email)

            mock_cache_set.assert_called_once_with(cache_key, True, timeout=30 * 60)

    async def test_cached_email_validator_cache_key_generation(self):
        """Тест генерації ключа кешу"""
        email = 'test@example.com'
        expected_cache_key = f"email_valid_{hash(email)}"

        with patch('users.utils.validators.cache.get') as mock_cache_get:
            mock_cache_get.return_value = None

            with patch('users.utils.validators.cache.set') as mock_cache_set:
                await cached_email_validator(email)

                mock_cache_get.assert_called_once_with(expected_cache_key)
                mock_cache_set.assert_called_once_with(expected_cache_key, True, timeout=30 * 60)

    async def test_cached_email_validator_sync_to_async_calls(self):
        """Тест викликів sync_to_async"""
        email = 'test@example.com'

        with patch('users.utils.validators.sync_to_async') as mock_sync_to_async:
            async def mock_cache_get(key):
                return None

            async def mock_cache_set(key, value, timeout):
                return None

            async def mock_email_validator(email):
                return None

            mock_sync_to_async.side_effect = [
                mock_cache_get,
                mock_email_validator,
                mock_cache_set
            ]

            result = await cached_email_validator(email)

            self.assertTrue(result)
            self.assertEqual(mock_sync_to_async.call_count, 3)

    def test_email_validator_instance_type(self):
        """Тест типу email валідатора"""
        from django.core.validators import EmailValidator
        self.assertIsInstance(email_validator, EmailValidator)

    def test_phone_validator_instance_type(self):
        """Тест типу phone валідатора"""
        from django.core.validators import RegexValidator
        self.assertIsInstance(phone_validator, RegexValidator)

    def test_phone_validator_regex_pattern(self):
        """Тест regex патерну phone валідатора"""
        expected_pattern = r'^\+?[0-9]{10,15}$'
        self.assertEqual(phone_validator.regex.pattern, expected_pattern)

    async def test_cached_email_validator_different_emails_different_cache_keys(self):
        """Тест що різні email мають різні ключі кешу"""
        email1 = 'test1@example.com'
        email2 = 'test2@example.com'

        cache_key1 = f"email_valid_{hash(email1)}"
        cache_key2 = f"email_valid_{hash(email2)}"

        self.assertNotEqual(cache_key1, cache_key2)

        await cached_email_validator(email1)
        await cached_email_validator(email2)

        self.assertTrue(cache.get(cache_key1))
        self.assertTrue(cache.get(cache_key2))

    async def test_cached_email_validator_return_value(self):
        """Тест що cached_email_validator завжди повертає True для валідних email"""
        valid_emails = [
            'test@example.com',
            'user@domain.org',
            'valid@email.co.uk'
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                result = await cached_email_validator(email)
                self.assertTrue(result)

    @patch('users.utils.validators.email_validator')
    async def test_cached_email_validator_exception_handling(self, mock_email_validator):
        """Тест обробки винятків в cached_email_validator"""
        email = 'test@example.com'

        mock_email_validator.side_effect = ValidationError('Test error')

        with self.assertRaises(ValidationError):
            await cached_email_validator(email)

        cache_key = f"email_valid_{hash(email)}"
        self.assertFalse(cache.get(cache_key))

    async def test_cached_email_validator_concurrent_access(self):
        """Тест одночасного доступу до кешованого валідатора"""
        email = 'concurrent@example.com'

        tasks = [cached_email_validator(email) for _ in range(5)]
        results = await asyncio.gather(*tasks)

        self.assertTrue(all(results))

    async def test_cached_email_validator_memory_usage(self):
        """Тест використання пам'яті кешем"""
        emails = [f'test{i}@example.com' for i in range(100)]

        for email in emails:
            await cached_email_validator(email)

        for email in emails:
            cache_key = f"email_valid_{hash(email)}"
            self.assertTrue(cache.get(cache_key))

    def test_phone_validator_edge_cases(self):
        """Тест граничних випадків для phone валідатора"""
        edge_cases = [
            ('+1234567890', True),
            ('1234567890', True),
            ('+123456789012345', True),
            ('123456789012345', True),
            ('+123456789', False),
            ('123456789', False),
            ('+1234567890123456', False),
            ('1234567890123456', False),
        ]

        for phone, should_be_valid in edge_cases:
            with self.subTest(phone=phone):
                if should_be_valid:
                    try:
                        phone_validator(phone)
                    except ValidationError:
                        self.fail(f'Valid phone {phone} was rejected')
                else:
                    with self.assertRaises(ValidationError):
                        phone_validator(phone)

    async def test_cached_email_validator_cache_miss_then_hit(self):
        """Тест послідовності cache miss -> cache hit"""
        email = 'test@example.com'
        cache_key = f"email_valid_{hash(email)}"

        with patch('users.utils.validators.email_validator') as mock_validator:
            result1 = await cached_email_validator(email)
            self.assertTrue(result1)
            mock_validator.assert_called_once()

        with patch('users.utils.validators.email_validator') as mock_validator:
            result2 = await cached_email_validator(email)
            self.assertTrue(result2)
            mock_validator.assert_not_called()

    def test_email_validator_boundary_cases(self):
        """Тест граничних випадків для email"""
        boundary_cases = [
            ('a@b.co', True),
            ('test@sub.domain.com', True),
            ('user+filter@domain.com', True),
            ('user@domain-name.com', True),
            ('123@456.789', True),
        ]

        for email, should_be_valid in boundary_cases:
            with self.subTest(email=email):
                if should_be_valid:
                    try:
                        email_validator(email)
                    except ValidationError:
                        self.fail(f'Valid email {email} was rejected')
                else:
                    with self.assertRaises(ValidationError):
                        email_validator(email)


class TestValidatorsIntegration(TestCase):
    """Інтеграційні тести для валідаторів"""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_run_async_cached_email_validator(self):
        """Тест запуску async функції в синхронному контексті"""

        async def run_test():
            return await cached_email_validator('test@example.com')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_test())
            self.assertTrue(result)
        finally:
            loop.close()
