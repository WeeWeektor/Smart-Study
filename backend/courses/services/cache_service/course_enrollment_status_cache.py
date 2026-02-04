from asgiref.sync import sync_to_async
from django.core.cache import caches

from common.services import register_cache_key

CACHE_TIMEOUT = 60 * 10


async def get_course_enrollment_status_cache_key(course_id) -> str:
    key = f"course_enrollment_status_by_id_{course_id}"

    await register_cache_key(key, "courses_get")
    return key


async def get_course_enrollment_status_cache(course_id, user_id):
    cache = caches["courses_get"]
    cache_key = await get_course_enrollment_status_cache_key(course_id)

    cached_data = await sync_to_async(lambda: cache.get(cache_key, version=1))()
    if cached_data:
        return cached_data

    from courses.services.course_by_user import get_course_enrollment_status
    data = await get_course_enrollment_status(course_id, user_id)

    if data.get("is_fully_completed") or data.get("is_failed"):
        await sync_to_async(lambda: cache.set(cache_key, data, CACHE_TIMEOUT, version=1))()

    return data


async def invalidate_course_enrollment_status_cache(course_id) -> bool:
    cache = caches["courses_get"]
    cache_key = await get_course_enrollment_status_cache_key(course_id)
    return await sync_to_async(lambda: cache.delete(cache_key, version=1))()
