from asgiref.sync import sync_to_async

from common.utils import success_response
from courses.services import validate_test_data


async def update_test(data: dict, test_id, test_type: str, all_new_questions_data: bool) -> dict:
    validate_test_data(data, test_type)

    from courses.services.test_actions_service import prepare_test_for_action
    test, data_id_fk = await prepare_test_for_action(test_id, test_type, action="edit")

    updated_fields = update_fields(test, data)



async def save_test(test, updated_fields: list) -> dict:
    await sync_to_async(test.save)(update_fields=updated_fields)

    return success_response({
        "data": "Test updated successfully.",
        "test_id": str(test.id),
    })


def update_fields(test, data: dict) -> list:
    """Оновлення полів тесту"""
    updated_fields = []

    for field, value in data.items():
        if hasattr(test, field) and getattr(test, field) != value:
            setattr(test, field, value)
            updated_fields.append(field)

    return updated_fields
