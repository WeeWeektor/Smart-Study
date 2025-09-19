from asgiref.sync import sync_to_async

from common.services import mongo_repo
from courses.models import Test
from courses.services import validate_test_data, validate_test_question_data
from courses.services.cache_service import invalidate_instance_cached_all, invalidate_test_cache_by_course_or_module


async def create_test(test_type: str, user, data: dict, instance_type: str):
    validate_test_data(data, test_type)

    data_to_create_test = {
        "title": data["title"].strip(),
        "description": (data.get("description") or "").strip(),
        "time_limit": data.get("time_limit", 0),
        "count_attempts": data.get("count_attempts", 0),
        "pass_score": data.get("pass_score", 0),
        "randomize_questions": data.get("randomize_questions", False),
        "show_correct_answers": data.get("show_correct_answers", True),
    }

    test_config = {
        "public": {
            "is_public": True,
            "owner_id": user.id,
            "category": data.get("category"),
            "level": data.get("level"),
            "order": 1,
        },
        "course": {
            "course_id": data.get("course_id"),
            "is_public": False,
            "order": data.get("order", 1),
        },
        "module": {
            "module_id": data.get("module_id"),
            "is_public": False,
            "order": data.get("order", 1),
        },
    }

    if test_type not in test_config:
        raise TypeError(f"Unknown test type: {test_type}")

    data_to_create_test.update(test_config[test_type])

    questions_data = []
    for qd in data.get("questions", []):
        await sync_to_async(validate_test_question_data)(qd)
        questions_data.append({
            "question_text": qd["question_text"].strip(),
            "choices": qd.get("choices", []),
            "correct_answers": qd.get("correct_answers", []),
            "points": qd.get("points", 1),
            "order": qd.get("order"),
        })

    mongo_document_id = await sync_to_async(lambda: mongo_repo.insert_document(
        "questions_data_for_test", {"questions": questions_data}
    ))()
    data_to_create_test["test_data_ids"] = mongo_document_id

    test_created = await sync_to_async(Test.objects.create)(**data_to_create_test)

    cache_invalidator = {
        "public": lambda: invalidate_instance_cached_all(
            instance_type=f"{instance_type} test",
            instance_type_cache="public_tests_get",
            category=test_created.category,
            level=test_created.level,
            author_id=user.id
        ),
        "course": lambda: invalidate_test_cache_by_course_or_module(
            instance_id=str(test_created.id),
            instance_type=f"{instance_type} test",
        ),
        "module": lambda: invalidate_test_cache_by_course_or_module(
            instance_id=str(test_created.id),
            instance_type=f"{instance_type} test",
        ),
    }

    await sync_to_async(cache_invalidator[test_type], thread_sensitive=True)()
    return test_created
