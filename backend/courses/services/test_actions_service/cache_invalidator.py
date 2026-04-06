def cache_invalidators(test_type: str, test, user=None):
    from courses.services.cache_service import invalidate_instance_cached_all, invalidate_test_cache_by_course_or_module
    invalidators = {
        "public": lambda: invalidate_instance_cached_all(
            instance_type="public test",
            instance_type_cache="public_tests_get",
            category=test.category,
            level=test.level,
            author_id=user.id
        ),
        "course": lambda: invalidate_test_cache_by_course_or_module(
            instance_id=str(test.id),
            instance_type="course test",
        ),
        "module": lambda: invalidate_test_cache_by_course_or_module(
            instance_id=str(test.id),
            instance_type="module test",
        ),
    }

    return invalidators[test_type]
