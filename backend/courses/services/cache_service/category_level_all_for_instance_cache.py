import logging
from typing import Union

from asgiref.sync import sync_to_async
from django.core.cache import caches
from django.utils.translation import gettext

from common.services import register_cache_key
from common.utils import error_response

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60


async def get_cache_key(
        instance_type: str,
        instance_type_cache: str,
        cate: Union[list, None] = None,
        level: Union[str, None] = None
) -> str:
    if isinstance(cate, list):
        category_str = ';'.join(sorted(cate))
        if level is None:
            key = f'{instance_type}_{category_str}_category'
        else:
            key = f'{instance_type}_{category_str}_category_{level}_level'
    else:
        if level is None:
            key = f'all_{instance_type}'
        else:
            key = f'{instance_type}_{level}_level'

    await register_cache_key(key, instance_type_cache)
    return key


async def get_instance_cached_all(
        instance_type: str,
        instance_type_cache: str,
        cate: Union[list, None] = None,
        level: Union[str, None] = None
) -> Union[dict, list]:
    instance_cache = caches[f"{instance_type_cache}"]
    cache_key = await get_cache_key(instance_type, instance_type_cache, cate, level)

    cached_data = await sync_to_async(lambda: instance_cache.get(cache_key, default=None, version=1))()
    if cached_data:
        return cached_data

    if instance_type == "courses":
        from courses.services.course_actions_service import get_courses
        instance_data = await get_courses(cate, level)
    elif instance_type == "public test":
        from courses.services.test_actions_service import get_public_tests
        instance_data = await get_public_tests(cate, level)
    else:
        logger.error(gettext("Unsupported instance type for caching"))
        return error_response(gettext("Unsupported instance type for caching"), status=400)

    await sync_to_async(lambda: instance_cache.set(cache_key, instance_data, CACHE_TIMEOUT, version=1))()
    return instance_data
