from asgiref.sync import sync_to_async

from common.services import mongo_repo
from courses.services.structure_course_module_action_service.structure_utils import get_structure_ids_obj


async def add_data_to_structure(target_type: str, target_id: str, structure_type: str, structure_data: dict):
    """
        Універсальний метод для додавання структур:
        - course: додає module або lesson
        - module: додає lesson або test
    """

    structure_ids_obj = await get_structure_ids_obj(target_type, target_id)

    await sync_to_async(mongo_repo.update_document)(
        collection_name=f"{target_type}_structures",
        doc_id=str(structure_ids_obj.structure_ids),
        update_data={
            "structure": {
                "type": structure_type,
                **structure_data
            }
        },
        action="push"
    )
