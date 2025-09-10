import logging
import uuid

from asgiref.sync import sync_to_async
from django.core.cache import caches
from django.utils.translation import gettext

from common.services import register_cache_key
from common.utils import error_response

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60


async def get_instance_by_id_cache_key(instance_id: uuid.UUID, instance_type: str, instance_type_cache: str) -> str:
    key = f"{instance_type}_by_id_{instance_id}"

    await register_cache_key(key, instance_type_cache)
    return key


async def get_cached_instance_by_id(
        instance_type: str,
        instance_type_cache: str,
        instance_id: uuid.UUID
):
    instance_cache = caches[f"{instance_type_cache}"]
    cache_key = await get_instance_by_id_cache_key(instance_id, instance_type, instance_type_cache)

    cached_data = await sync_to_async(lambda: instance_cache.get(cache_key, default=None, version=1))()
    if cached_data:
        return cached_data

    if instance_type == "course":
        from courses.services import get_course_by_id
        instance_data = await get_course_by_id(instance_id)
    else:
        logger.error(gettext("Unsupported instance type for caching"))
        return error_response(gettext("Unsupported instance type for caching"), status=400)

    if instance_data["course"]["is_published"]:
        await sync_to_async(lambda: instance_cache.set(cache_key, instance_data, CACHE_TIMEOUT, version=1))()

    return instance_data


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
