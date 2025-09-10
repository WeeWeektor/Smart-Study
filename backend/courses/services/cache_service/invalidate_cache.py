from asgiref.sync import sync_to_async
from django.core.cache import caches


async def invalidate_instance_cached_all(
        instance_type: str,
        instance_type_cache: str,
        category: str | None,
        level: str | None,
        author_id: str | None
) -> None:
    """
    Інвалідує всі кеші для instance_type.
    Видаляє всі ключі, які містять категорію, левел або id автора.
    """
    instance_cache = caches[f"{instance_type_cache}"]

    keys: set[str] = await sync_to_async(lambda: instance_cache.get("all_cache_keys", set()))()
    if not keys:
        return

    to_delete = set()

    for key in keys:
        if (category and level) and (category in key and f"_{level}_level" in key):
            to_delete.add(key)
        elif category and category in key:
            to_delete.add(key)
        elif level and f"_{level}_level" in key:
            to_delete.add(key)
        elif author_id and author_id in key:
            to_delete.add(key)

    to_delete.add(f'all_{instance_type}')

    def delete_keys(keys_to_delete):
        for k in keys_to_delete:
            instance_cache.delete(k)

    await sync_to_async(delete_keys)(to_delete)

    keys -= to_delete

    await sync_to_async(lambda: instance_cache.set("all_cache_keys", keys, None))()






