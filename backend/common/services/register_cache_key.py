from asgiref.sync import sync_to_async
from django.core.cache import caches


async def register_cache_key(key: str, instance_type_cache: str):
    """Зберігає ключ кешу в спеціальному наборі для можливості його інвалідації пізніше."""
    instance_cache = caches[f"{instance_type_cache}"]

    keys = await sync_to_async(lambda: instance_cache.get('all_cache_keys', set()))()
    if key not in keys:
        keys.add(key)
        await sync_to_async(lambda: instance_cache.set("all_cache_keys", keys, 3600*12))()
