from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from common.services import mongo_repo
from common.utils import success_response
from courses.services import validate_test_data
from courses.services.structure_course_module_action_service import update_data_in_structure


def success_response_info(test):
    return success_response({
        "data": _("Test updated successfully."),
        "test_id": str(test.id),
    })


async def update_test(data: dict, test_id, test_type: str, all_new_questions_data: bool) -> dict:
    validate_test_data(data, test_type)

    from courses.services.test_actions_service import prepare_test_for_action
    test = await prepare_test_for_action(test_id, test_type, action="edit")

    updated_fields = update_fields(test, data)

    if all_new_questions_data:
        await _update_questions(test, data.get("questions", []), replace=True)
    elif "questions" in data:
        await _update_questions(test, data["questions"], replace=False)

    if updated_fields:
        await sync_to_async(test.save)(update_fields=updated_fields)

    if test_type in ("module", "course") and any(f in updated_fields for f in ("title", "order")):
        await update_data_in_structure(
            target_type=test_type,
            target_id=str(test.module_id if test_type == "module" else test.course_id),
            structure_data={"title": test.title, "order": test.order},
            identifier_field="test_id",
            identifier_value=str(test.id)
        )

    return success_response_info(test)


async def _update_questions(test, questions, replace: bool = False):
    from courses.services.test_actions_service import prepare_questions_data
    new_questions_data = await prepare_questions_data(questions)
    if replace:
        await sync_to_async(mongo_repo.replace_document)(
            "questions_data_for_test",
            str(test.test_data_ids),
            {"questions": new_questions_data}
        )
    else:
        await sync_to_async(mongo_repo.update_document)(
            "questions_data_for_test",
            str(test.test_data_ids),
            {"questions": new_questions_data},
            action="set"
        )


def update_fields(test, data: dict) -> list:
    """Оновлення полів тесту"""
    updated_fields = []

    for field, value in data.items():
        if hasattr(test, field) and getattr(test, field) != value:
            setattr(test, field, value)
            updated_fields.append(field)

    return updated_fields
