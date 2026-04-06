from asgiref.sync import sync_to_async

from common.services import mongo_repo
from courses.services.structure_course_module_action_service.structure_utils import get_structure_ids_obj


async def remove_data_from_structure(target_type: str, target_id: str, filter_data: dict):
    """
        Універсальний метод для видалення структурних елементів з course/module:
        - course: видаляє module або lesson
        - module: видаляє lesson або test

        :param target_type: 'course' або 'module'
        :param target_id: UUID об'єкта Django
        :param filter_data: словник з полями для $pull (наприклад {'test_id': '1234'})
    """

    structure_ids_obj = await get_structure_ids_obj(target_type, target_id)

    await sync_to_async(mongo_repo.update_document)(
        collection_name=f"{target_type}_structures",
        doc_id=str(structure_ids_obj.structure_ids),
        update_data={"structure": filter_data},
        action="pull"
    )
