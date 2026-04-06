from asgiref.sync import sync_to_async

from common.services import mongo_repo
from courses.services.structure_course_module_action_service.structure_utils import get_structure_ids_obj


async def update_data_in_structure(
        target_type: str,
        target_id: str,
        structure_data: dict,
        identifier_field: str,
        identifier_value
):
    """
    Універсальний метод для оновлення існуючих елементів у структурі (масиві 'structure'):
    - target_type: 'course' або 'module'
    - target_id: ID об'єкта Django
    - structure_data: дані для оновлення
    - identifier_field: поле для ідентифікації елемента у масиві (наприклад, 'test_id')
    - identifier_value: значення для пошуку у масиві
    """

    structure_ids_obj = await get_structure_ids_obj(target_type, target_id)

    array_filters = [{"elem." + identifier_field: identifier_value}]

    update_data = {f"structure.$[elem].{k}": v for k, v in structure_data.items()}

    await sync_to_async(mongo_repo.update_document)(
        collection_name=f"{target_type}_structures",
        doc_id=str(structure_ids_obj.structure_ids),
        update_data=update_data,
        action="set",
        array_filters=array_filters
    )
