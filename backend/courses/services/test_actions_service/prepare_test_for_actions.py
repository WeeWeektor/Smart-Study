import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from courses.models import Test
from courses.services import validate_test_question_data
from courses.services.test_actions_service import cache_invalidators, validate_test_editable

TEST_FETCH_STRATEGIES = {
    "module": lambda test_id: Test.objects.select_related("module").get(pk=test_id),
    "course": lambda test_id: Test.objects.select_related("course").get(pk=test_id),
    "public": lambda test_id: Test.objects.select_related("owner").get(pk=test_id),
}


async def prepare_test_for_action(test_id, test_type: str, action: str):
    if test_type not in TEST_FETCH_STRATEGIES:
        raise ValidationError(_("Invalid test type"))

    test = await sync_to_async(TEST_FETCH_STRATEGIES[test_type])(test_id)

    data = {}
    if test_type == "course" and test.course_id:
        data["course_id"] = str(test.course_id)
    elif test_type == "module" and test.module_id:
        data["module_id"] = str(test.module_id)
    elif test_type == "public" and test.owner:
        data["owner"] = test.owner
    else:
        raise ValidationError(_("Invalid test type"))

    error = await validate_test_editable(test_type, data, action=action)
    if error:
        data = json.loads(error.content)
        message = data.get("message", _("Unknown error"))
        raise ValidationError(message)

    await sync_to_async(
        cache_invalidators(test_type, test, data["owner"] if "owner" in data else None),
        thread_sensitive=True
    )()

    return test


async def prepare_questions_data(questions: list[dict]) -> list[dict]:
    """Валідує та форматує список питань для збереження у mongodb"""
    questions_data = []
    for qd in questions:
        question_type = 'single' if len(qd.get('correct_answers', [])) == 1 else 'multiple'
        await sync_to_async(validate_test_question_data)(qd)
        questions_data.append({
            "questionText": qd["questionText"].strip(),
            "choices": qd.get("choices", []),
            "correct_answers": qd.get("correct_answers", []),
            "points": qd.get("points", 1),
            "order": qd.get("order"),
            "explanation": qd.get("explanation", ""),
            "image_url": qd.get("imageFileKey", ""),
            "type": question_type
        })

    return questions_data
