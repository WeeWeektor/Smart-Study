from asgiref.sync import sync_to_async

from common.services import mongo_repo
from common.utils import validate_uuid
from courses.models import Module
from courses.services import validate_module_data
from courses.services.structure_course_module_action_service import add_data_to_structure


async def create_module(data: dict, course_id):
    uuid_obj = validate_uuid(course_id)
    validate_module_data(data)

    structure_ids = await sync_to_async(mongo_repo.insert_document)("module_structures", {})

    # TODO можливо для зміни модуля зробити як в створенні відгуку про курс в методі create_review_of_course
    module_create = await sync_to_async(Module.objects.create)(
        course_id=uuid_obj,
        title=data["title"].strip(),
        order=data["order"],
        structure_ids=structure_ids
    )

    await add_data_to_structure(
        target_type="course",
        target_id=data.get("course_id"),
        structure_type="module",
        structure_data={
            "module_id": str(module_create.id),
            "title": module_create.title,
            "order": module_create.order
        }
    )

    return module_create
