import logging

from django.core.cache import caches

logger = logging.getLogger(__name__)

courses_cache = caches["public_tests"]

ALL_PUBLIC_TESTS_CACHE_TIMEOUT = 60 * 60 * 1

def get_all_public_tests_cache_key():
    pass


async def get_cached_all_tests():
    pass

async def invalidate_all_tests_cache():
    pass
