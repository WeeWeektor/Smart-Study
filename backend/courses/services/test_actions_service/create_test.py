from asgiref.sync import sync_to_async

from common.services import mongo_repo
from courses.models import Test
from courses.services import validate_test_data


async def create_test(test_type: str, user, data: dict):
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

    from courses.services.test_actions_service import prepare_questions_data, cache_invalidators
    questions_data = await prepare_questions_data(data.get("questions", []))

    mongo_document_id = await sync_to_async(lambda: mongo_repo.insert_document(
        "questions_data_for_test", {"questions": questions_data}
    ))()
    data_to_create_test["test_data_ids"] = mongo_document_id

    test_created = await sync_to_async(Test.objects.create)(**data_to_create_test)

    await sync_to_async(
        cache_invalidators(test_type, test_created, user),
        thread_sensitive=True
    )()

    return test_created
