import logging
from typing import Union

from asgiref.sync import sync_to_async
from django.core.cache import caches
from django.utils.translation import gettext

from common.utils import error_response

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 15


def get_cache_key(instance_type: str, author_id: str) -> str:
    return f"{instance_type}_by_author_{author_id}"


async def get_instance_cached_by_author_id(instance_type: str,
                                           instance_type_cache: str,
                                           author_id: str
                                           ) -> Union[dict, list]:
    instance_cache = caches[f"{instance_type_cache}_get"]
    cache_key = get_cache_key(instance_type, author_id)

    cached_data = await sync_to_async(lambda: instance_cache.get(cache_key, default=None, version=1))()
    if cached_data:
        return cached_data

    if instance_type == "courses":
        from courses.services import get_published_courses_by_autor
        instance_data = await get_published_courses_by_autor(author_id)
    else:
        logger.error(gettext("Unsupported instance type for caching"))
        return error_response(gettext("Unsupported instance type for caching"), status=400)

    await sync_to_async(lambda: instance_cache.set(cache_key, instance_data, CACHE_TIMEOUT, version=1))()
    return instance_data


async def invalidate_instance_cached_by_author_id(instance_type: str,
                                                  instance_type_cache: str,
                                                  author_id: str
                                                  ) -> bool:
    instance_cache = caches[f"{instance_type_cache}_get"]
    cache_key = get_cache_key(instance_type, author_id)
    result = await sync_to_async(lambda: instance_cache.delete(cache_key, version=1))()
    logger.info(
        f"{gettext(f'Invalidating {instance_type} existence cache by author:')} "
        f"{author_id} - {gettext('successfully') if result else gettext('key not found')}"
    )
    return result
