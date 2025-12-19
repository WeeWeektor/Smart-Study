from asgiref.sync import sync_to_async
from django.core.cache import caches

from common.services import register_cache_key
from courses.services.course_review_actions_service import get_course_review

CACHE_TIMEOUT = 60 * 20


async def get_course_review_cache_key(course_id) -> str:
    key = f"course_review_by_id_{course_id}"

    await register_cache_key(key, "courses_get")
    return key


async def get_course_review_cache(course_id):
    cache = caches["courses_get"]
    cache_key = await get_course_review_cache_key(course_id)

    cached_data = await sync_to_async(lambda: cache.get(cache_key, version=1))()
    if cached_data:
        return cached_data

    course_reviews = await get_course_review(course_id)
    await sync_to_async(lambda: cache.set(cache_key, course_reviews, CACHE_TIMEOUT, version=1))()

    return course_reviews


async def invalidate_course_review_cache(course_id) -> bool:
    cache = caches["courses_get"]
    cache_key = await get_course_review_cache_key(course_id)
    return await sync_to_async(lambda: cache.delete(cache_key, version=1))()
