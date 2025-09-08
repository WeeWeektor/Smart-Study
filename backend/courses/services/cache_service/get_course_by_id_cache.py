import logging

from asgiref.sync import sync_to_async
from django.core.cache import caches
from django.utils.translation import gettext

from courses.models import Course, CourseMeta
from courses.services import build_course_json_success, build_course_json_failure
from users.models import CustomUser

logger = logging.getLogger(__name__)

courses_cache = caches["courses_get"]

COURSE_BY_ID_CACHE_TIMEOUT = 60 * 60


def get_course_by_id_cache_key(course_id):
    return f"course_by_id_{course_id}"


async def get_cached_course_by_id(course):
    cache_key = get_course_by_id_cache_key(course.id)
    cached_data = await sync_to_async(lambda: courses_cache.get(cache_key, default=None, version=1))()

    if cached_data:
        return cached_data

    try:
        course_with_details = await sync_to_async(
            lambda: Course.objects.select_related('details', 'owner').get(id=course.id)
        )()
        course_details = await sync_to_async(
            lambda: CourseMeta.objects.get(id=course_with_details.details.id)
        )()
        course_owner = await sync_to_async(
            lambda: CustomUser.objects.get(id=course_with_details.owner.id)
        )()

        course_data = build_course_json_success(course_with_details, course_details, course_owner)

        await sync_to_async(lambda: courses_cache.set(cache_key, course_data, COURSE_BY_ID_CACHE_TIMEOUT, version=1))()
        return course_data

    except Exception as e:
        logger.error(f"{gettext('Error receiving course by id')} ({course.id}): {str(e)}")
        return build_course_json_failure(course)


async def invalidate_cached_course_by_id(course):
    cache_key = get_course_by_id_cache_key(course.id)
    result = await sync_to_async(lambda: courses_cache.delete(cache_key, version=1))()
    logger.info(
        f"{gettext('Invalidating course existence cache by id:')} "
        f"{course.id} - "
        f"{gettext('successfully') if result else gettext('key not found')}"
    )
    return result
