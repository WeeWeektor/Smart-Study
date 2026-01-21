from asgiref.sync import sync_to_async
from django.core.cache import caches

from common.services import register_cache_key
from courses.services.course_by_user import get_courses_by_user

CACHE_TIMEOUT = 60 * 60


async def courses_by_user_id_cache_key(user_id) -> str:
    key = f"courses_by_user_id_{user_id}"

    await register_cache_key(key, "courses_get")
    return key


async def courses_by_user_id_cache(user_id):
    cache = caches["courses_get"]
    cache_key = await courses_by_user_id_cache_key(user_id)

    cached_data = await sync_to_async(lambda: cache.get(cache_key, version=1))()
    if cached_data:
        return cached_data

    courses_by_user = await get_courses_by_user(user_id)
    await sync_to_async(lambda: cache.set(cache_key, courses_by_user, CACHE_TIMEOUT, version=1))()

    return courses_by_user


async def invalidate_courses_by_user_id_cache(user_id) -> bool:
    cache = caches["courses_get"]
    cache_key = await courses_by_user_id_cache_key(user_id)
    return await sync_to_async(lambda: cache.delete(cache_key, version=1))()
