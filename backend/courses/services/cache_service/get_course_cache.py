import logging

from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.utils.translation import gettext

from courses.models import Course, CourseMeta
from courses.services import build_course_json_success, build_course_json_failure
from users.models import CustomUser

logger = logging.getLogger(__name__)

COURSE_BY_ID_CACHE_TIMEOUT = 60 * 60


def get_course_by_id_cache_key(course_id):
    return f"course_by_id_{course_id}"


async def get_cached_course_by_id(course):
    cache_key = get_course_by_id_cache_key(course.id)
    cached_data = await sync_to_async(cache.get)(cache_key, default=None, version=1)

    if cached_data:
        return cached_data

    try:
        course_with_details = await sync_to_async(
            Course.objects.select_related('details', 'owner').get
        )(id=course.id)

        course_details, _ = await (sync_to_async(CourseMeta.objects.get)
                                   (id=course_with_details.details.id, defaults=None))
        course_owner, _ = await sync_to_async(CustomUser.objects.get)(id=course_with_details.owner.id, defaults=None)

        course_data = build_course_json_success(course_with_details, course_details, course_owner)

        await sync_to_async(cache.set)(cache_key, course_data, COURSE_BY_ID_CACHE_TIMEOUT, version=1)
        return course_data

    except Exception as e:
        logger.error(f"{gettext("Error receiving course by id")} ({course.id}): {str(e)}")
        return build_course_json_failure(course)


async def invalidate_cached_course_by_id(course):
    cache_key = get_course_by_id_cache_key(course.id)
    result = await sync_to_async(cache.delete)(cache_key, version=1)
    logger.info(
        f"{gettext("Invalidating course existence cache by id:")} {course.id} - {
           gettext("successfully") if result else gettext("key not found")
        }")
    return result
