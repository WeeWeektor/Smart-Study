from django.core.cache import caches


def invalidate_instance_cached_all(
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
    instance_cache = caches[instance_type_cache]

    keys: set[str] = instance_cache.get("all_cache_keys", set())
    if not keys:
        return

    to_delete = set()

    for key in keys:
        if author_id and str(author_id) in key:
            to_delete.add(key)
            continue

        key_has_category = category and str(category) in key
        key_has_level = level and f"_{level}_level" in key

        if key_has_category:
            add_key = _match_key_with_category_and_level(level, key, key_has_level)
            if add_key:
                to_delete.add(add_key)

    to_delete.add(f'all_{instance_type}')

    for k in to_delete:
        instance_cache.delete(k)

    keys -= to_delete
    instance_cache.set("all_cache_keys", keys, 3600*12)


def _match_key_with_category_and_level(level: str, key: str, key_has_level: bool) -> str | None:
    if level:
        if key_has_level:
            return key
        else:
            if "_level" not in key:
                return key
    else:
        return key

def invalidate_test_cache_by_course_or_module(instance_id: str, instance_type: str) -> None:
    instance_cache = caches["courses_get"]

    keys: set[str] = instance_cache.get("all_cache_keys", set())
    if not keys:
        return
    key = f"{instance_type}_by_id_{instance_id}"

    instance_cache.delete(key)
    if key in keys:
        keys.discard(key)
        instance_cache.set("all_cache_keys", keys, 3600 * 12)
