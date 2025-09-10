import logging
from typing import Union

from asgiref.sync import sync_to_async
from django.core.cache import caches
from django.utils.translation import gettext

from common.utils import error_response

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60


def get_cache_key(
        instance_type: str,
        cate: Union[list, None] = None,
        level: Union[str, None] = None
) -> str:
    if isinstance(cate, list):
        category_str = ';'.join(sorted(cate))
        if level is None:
            return f'{instance_type}_{category_str}_category'
        else:
            return f'{instance_type}_{category_str}_category_{level}_level'
    else:
        if level is None:
            return f'all_{instance_type}'
        else:
            return f'{instance_type}_{level}_level'


async def get_instance_cached_all(
        instance_type: str,
        instance_type_cache: str,
        cate: Union[list, None] = None,
        level: Union[str, None] = None
) -> Union[dict, list]:
    instance_cache = caches[f"{instance_type_cache}_get"]
    cache_key = get_cache_key(instance_type, cate, level)

    cached_data = await sync_to_async(lambda: instance_cache.get(cache_key, default=None, version=1))()
    if cached_data:
        return cached_data

    if instance_type == "courses":
        from courses.services import get_courses
        instance_data = await get_courses(cate, level)
    else:
        logger.error(gettext("Unsupported instance type for caching"))
        return error_response(gettext("Unsupported instance type for caching"), status=400)

    await sync_to_async(lambda: instance_cache.set(cache_key, instance_data, CACHE_TIMEOUT, version=1))()
    return instance_data


async def invalidate_instance_cached_all(
        instance_type: str,
        instance_type_cache: str,
        cate: Union[list, None] = None,
        level: Union[str, None] = None
) -> bool:
    instance_cache = caches[f"{instance_type_cache}_get"]
    cache_key = get_cache_key(instance_type, cate, level)
    result = await sync_to_async(lambda: instance_cache.delete(cache_key, version=1))()
    logger.info(
        f"{gettext(f'Invalidating {instance_type} existence cache by category:')} "
        f"{cate}{f", and {level} level" if level is not None else ''} - "
        f"{gettext('successfully') if result else gettext('key not found')}"
    )
    return result
