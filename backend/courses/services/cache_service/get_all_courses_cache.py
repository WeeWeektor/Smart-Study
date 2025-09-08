import logging
from typing import Union

from asgiref.sync import sync_to_async
from django.core.cache import caches
from django.utils.translation import gettext

from courses.models import Course, CourseMeta
from courses.services import build_course_json_success
from users.models import CustomUser

logger = logging.getLogger(__name__)

courses_cache = caches["courses_get"]

ALL_COURSES_CACHE_TIMEOUT = 60 * 60 * 2


def get_all_courses_cache_key(courses_category: Union[str, list, None] = None):
    if courses_category is None:
        return 'courses_all_categories'
    elif isinstance(courses_category, list):
        category_str = ",".join(sorted(courses_category))
        return f"all_courses_{category_str}"
    elif isinstance(courses_category, str):
        return f"all_courses_{courses_category}"


async def get_cached_all_courses(courses_category: Union[str, list, None] = None):
    cache_key = get_all_courses_cache_key(courses_category)
    cached_data = await sync_to_async(lambda: courses_cache.get(cache_key, default=None, version=1))()
    if cached_data:
        return cached_data

    if isinstance(courses_category, list):
        categories = courses_category
    elif isinstance(courses_category, str):
        categories = [courses_category]
    else:
        categories = []

    try:
        if not categories:
            courses = await sync_to_async(lambda: list(Course.objects.select_related("details", 'owner').all()))()
        else:
            courses = await sync_to_async(lambda: list(
                Course.objects.select_related("details", 'owner').filter(category__in=categories)
            ))()

        details_ids = [c.details.id for c in courses if getattr(c, 'details', None)]
        owner_ids = [c.owner.id for c in courses if getattr(c, 'owner', None)]

        course_details = await sync_to_async(lambda: list(CourseMeta.objects.filter(id__in=details_ids)))()
        course_owners = await sync_to_async(lambda: list(CustomUser.objects.filter(id__in=owner_ids)))()

        details_map = {d.id: d for d in course_details}
        owners_map = {o.id: o for o in course_owners}

        course_data = []
        for c in courses:
            details = details_map.get(c.details.id) if getattr(c, "details", None) else None
            owner = owners_map.get(c.owner.id) if getattr(c, "owner", None) else None

            course_data.append(
                build_course_json_success(c, details, owner)
            )

        await sync_to_async(lambda: courses_cache.set(cache_key, course_data, ALL_COURSES_CACHE_TIMEOUT, version=1))()
        return course_data

    except Exception as e:
        logger.error(
            f"{gettext('Error receiving course with category: ')} "
            f"({categories if categories else gettext('all')}): {str(e)}"
        )
        return {"courses": [], "error": gettext("Error retrieving courses")}


async def invalidate_cached_all_courses(courses_category: Union[str, list, None] = None):
    cache_key = get_all_courses_cache_key(courses_category)
    result = await sync_to_async(lambda: courses_cache.delete(cache_key, version=1))()
    logger.info(
        f"{gettext('Invalidating course existence cache by category:')} "
        f"{courses_category if courses_category else gettext('all')} - "
        f"{gettext('successfully') if result else gettext('key not found')}"
    )
    return result
