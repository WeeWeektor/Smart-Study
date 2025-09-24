from asgiref.sync import sync_to_async

from common.services import mongo_repo
from common.utils import validate_uuid
from courses.models import Module
from courses.services import validate_module_data


async def create_module(data: dict, course_id):
    uuid_obj = validate_uuid(course_id)
    validate_module_data(data)

    structure_ids = await sync_to_async(mongo_repo.insert_document)("module_structures", {})

    module_create = await sync_to_async(Module.objects.create)(
        course_id=uuid_obj,
        title=data["title"].strip(),
        order=data["order"],
        structure_ids=structure_ids
    )

    return module_create
