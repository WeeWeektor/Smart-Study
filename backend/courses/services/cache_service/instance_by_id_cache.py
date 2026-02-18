import logging
import uuid

from asgiref.sync import sync_to_async
from django.core.cache import caches
from django.utils.translation import gettext

from common.services import register_cache_key
from common.utils import error_response
from courses.services.lesson_actions_service import get_lesson_by_id

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60
CACHE_TIMEOUT_TEST = 60 * 20
CACHE_TIMEOUT_LESSON = 60 * 20


async def get_instance_by_id_cache_key(instance_id: uuid.UUID, instance_type: str, instance_type_cache: str) -> str:
    key = f"{instance_type}_by_id_{instance_id}"

    await register_cache_key(key, instance_type_cache)
    return key


async def get_cached_instance_by_id(
        instance_type: str,
        instance_type_cache: str,
        instance_id: uuid.UUID,
        for_edit: "true" = None
):
    instance_cache = caches[f"{instance_type_cache}"]
    cache_key = await get_instance_by_id_cache_key(instance_id, instance_type, instance_type_cache)

    cached_data = await sync_to_async(lambda: instance_cache.get(cache_key, version=1))()
    if cached_data:
        return cached_data

    if instance_type == "course":
        from courses.services.course_actions_service import get_course_by_id
        instance_data = await get_course_by_id(instance_id, for_edit=for_edit)
    elif " test" in instance_type:
        from courses.services.test_actions_service import get_test_by_id
        if instance_type == "public test":
            instance_data = await get_test_by_id(instance_id, is_public=True)
        elif instance_type == "course test":
            instance_data = await get_test_by_id(instance_id, course=True)
        elif instance_type == "module test":
            instance_data = await get_test_by_id(instance_id, module=True)
        else:
            instance_data = None
    elif instance_type == "lesson":
        instance_data = await get_lesson_by_id(instance_id)
    else:
        logger.error(gettext("Unsupported instance type for caching"))
        return error_response(gettext("Unsupported instance type for caching"), status=400)

    timeout = _resolve_cache_timeout(instance_data)
    if timeout:
        await sync_to_async(lambda: instance_cache.set(cache_key, instance_data, timeout, version=1))()

    return instance_data


def _resolve_cache_timeout(instance_data: dict) -> int | None:
    """Визначає час кешування залежно від типу даних"""
    if instance_data.get("course", {}).get("is_published"):
        return CACHE_TIMEOUT
    if instance_data.get("public-test", {}).get("is_public"):
        return CACHE_TIMEOUT_TEST
    if instance_data.get("course-test", {}).get("course", {}).get("is_published"):
        return CACHE_TIMEOUT_TEST
    if instance_data.get("module-test", {}).get("module", {}).get("is_published"):
        return CACHE_TIMEOUT_TEST
    if instance_data.get("lesson", {}):
        return CACHE_TIMEOUT_LESSON
    return None


async def invalidate_cached_instance_by_id(instance_id: uuid.UUID,
                                           instance_type_cache: str,
                                           instance_type: str
                                           ) -> bool:
    instance_cache = caches[f"{instance_type_cache}"]
    cache_key = await get_instance_by_id_cache_key(instance_id, instance_type, instance_type_cache)
    result = await sync_to_async(lambda: instance_cache.delete(cache_key, version=1))()
    logger.info(
        f"{gettext(f'Invalidating {instance_type} existence cache by id:')} "
        f"{instance_id} - "
        f"{gettext('successfully') if result else gettext('key not found')}"
    )
    return result
