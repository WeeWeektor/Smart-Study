from asgiref.sync import sync_to_async
from django.core.cache import caches

from common.services import register_cache_key
from courses.services.course_recommendations_actions_service import get_course_recommendations

CACHE_TIMEOUT = 60 * 60 * 24


async def get_course_recommendations_cache_key(course_id, status_param) -> str:
    key = f"recommendations:{course_id}-{status_param}"

    await register_cache_key(key, "courses_get")
    return key


async def get_course_recommendations_cache(course_id, status_param, limit_param):
    cache = caches["courses_get"]
    cache_key = await get_course_recommendations_cache_key(course_id, status_param)

    cached_data = await sync_to_async(lambda: cache.get(cache_key, version=1))()
    if cached_data:
        return cached_data

    course_recommendations = await get_course_recommendations(course_id, status_param, limit_param)

    if course_recommendations:
        await sync_to_async(lambda: cache.set(cache_key, course_recommendations, CACHE_TIMEOUT, version=1))()

    return course_recommendations


async def invalidate_all_course_recommendations_cache():
    cache = caches["courses_get"]

    if hasattr(cache, "delete_pattern"):
        await sync_to_async(cache.delete_pattern)("recommendations:*")
    else:
        await sync_to_async(cache.clear)()
