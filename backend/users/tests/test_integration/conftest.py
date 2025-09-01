import pytest
from django.core.cache import cache
from django.test import override_settings

@pytest.fixture(autouse=True)
def clear_cache():
    """Очищення кешу перед кожним тестом"""
    cache.clear()
    yield
    cache.clear()

@pytest.fixture
def test_settings():
    """Налаштування для тестування"""
    with override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        CELERY_TASK_ALWAYS_EAGER=True,
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        },
        RATELIMIT_ENABLE=False,
        PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    ):
        yield

@pytest.fixture
def mock_supabase():
    """Mock Supabase для тестів"""
    from unittest.mock import patch
    with patch('users.user_utils.supabase') as mock:
        yield mock
