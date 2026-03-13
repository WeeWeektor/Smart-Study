from asgiref.sync import sync_to_async

from common.utils import validate_uuid
from courses.models import Module
from courses.services.structure_course_module_action_service import update_data_in_structure


async def update_module(module_id, module_data: dict):
    module_id = validate_uuid(module_id)

    if module_data.get("title") is None and module_data.get("order") is None:
        return

    module = await Module.objects.only('structure_ids', "title", "order").aget(id=module_id)

    if (module_data.get("title", module.title) == module.title
            and module_data.get("order", module.order) == module.order):
        return

    updated_mongo_data = {
        "title": module_data.get("title", module.title),
        "order": module_data.get("order", module.order)
    }

    await update_data_in_structure(
        target_type="course",
        target_id=str(module.course_id),
        structure_data=updated_mongo_data,
        identifier_field="module_id",
        identifier_value=str(module_id)
    )

    await sync_to_async(Module.objects.filter(id=module_id).update)(
        title=updated_mongo_data["title"],
        order=updated_mongo_data["order"]
    )
