import logging
from typing import Union

from asgiref.sync import sync_to_async
from django.core.cache import caches
from django.utils.translation import gettext

from common.services import register_cache_key
from common.utils import error_response

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 15


async def get_cache_key(instance_type: str, instance_type_cache: str, author_id: str) -> str:
    key = f"{instance_type}_by_author_{author_id}"

    await register_cache_key(key, instance_type_cache)
    return key


async def get_instance_cached_by_author_id(instance_type: str,
                                           instance_type_cache: str,
                                           author_id: str
                                           ) -> Union[dict, list]:
    instance_cache = caches[f"{instance_type_cache}"]
    cache_key = await get_cache_key(instance_type, instance_type_cache, author_id)

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
