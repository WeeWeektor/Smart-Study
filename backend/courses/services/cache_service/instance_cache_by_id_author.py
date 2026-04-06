import logging
from typing import Union

from asgiref.sync import sync_to_async
from django.core.cache import caches
from django.utils.translation import gettext

from common.services import register_cache_key
from common.utils import error_response

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 15


async def get_cache_key(instance_type: str, instance_type_cache: str, author_id: str,
                        sort_keys: Union[list, None] = None, status: str = None,
                        search_query: Union[str, None] = None
                        ) -> str:
    key = f"{instance_type}_by_author_{author_id}"
    if isinstance(sort_keys, list):
        key += f"_sort_{';'.join(sorted(sort_keys))}"
    if status and status == 'is_published':
        key += "_is_published"
    elif status and status == 'false':
        key += "_not_is_published"
    elif status and status == 'all':
        key += "_status_all"

    if search_query:
        key += f"_search_{search_query}"

    await register_cache_key(key, instance_type_cache)
    return key


async def get_instance_cached_by_author_id(instance_type: str,
                                           instance_type_cache: str,
                                           author_id: str,
                                           sort_keys: Union[list, None] = None,
                                           status: str = None,
                                           search_query: Union[str, None] = None
                                           ) -> Union[dict, list]:
    instance_cache = caches[instance_type_cache]
    cache_key = await get_cache_key(instance_type, instance_type_cache, author_id, sort_keys, status, search_query)

    cached_data = await sync_to_async(lambda: instance_cache.get(cache_key, default=None, version=1))()
    if cached_data:
        return cached_data

    if instance_type == "courses":
        from courses.services.course_actions_service import get_published_courses_by_autor
        instance_data = await get_published_courses_by_autor(author_id, sort_keys, status, search_query)
    elif instance_type == "public test":
        from courses.services.test_actions_service import get_public_tests_by_author
        instance_data = await get_public_tests_by_author(author_id)
    else:
        logger.error(gettext("Unsupported instance type for caching"))
        return error_response(gettext("Unsupported instance type for caching"), status=400)

    await sync_to_async(lambda: instance_cache.set(cache_key, instance_data, CACHE_TIMEOUT, version=1))()
    return instance_data


async def invalidate_author_cache(author_id: str, instance_type: str, instance_type_cache: str):
    instance_cache = caches[instance_type_cache]

    all_keys = await sync_to_async(lambda: instance_cache.get('all_cache_keys', set()))()

    if not all_keys:
        return

    target_prefix = f"{instance_type}_by_author_{author_id}"

    keys_to_delete = {key for key in all_keys if key.startswith(target_prefix)}

    if keys_to_delete:
        try:
            for key in keys_to_delete:
                await sync_to_async(instance_cache.delete)(key)

            remaining_keys = all_keys - keys_to_delete
            await sync_to_async(lambda: instance_cache.set("all_cache_keys", remaining_keys, 3600 * 12))()

            logger.info(f"Successfully invalidated {len(keys_to_delete)} keys for author {author_id}")
        except Exception as e:
            logger.error(f"Error while invalidating author cache: {str(e)}")
