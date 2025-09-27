from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from common.services import mongo_repo
from common.utils import success_response
from courses.models import Module
from courses.services.structure_course_module_action_service import remove_data_from_structure


async def remove_module(module_id):
    module = await sync_to_async(Module.objects.only("structure_ids").get)(pk=module_id)

    structure = await sync_to_async(mongo_repo.get_document_by_id)("module_structures", module.structure_ids)

    if structure and "structure" in structure:
        for item in structure["structure"]:
            if item.get("type") == "test" and "test_id" in item:
                from courses.services.test_actions_service.remove_test import remove_test
                await remove_test(item["test_id"], test_type="module")
            # elif item.get("type") == "lesson" and "lesson_id" in item:
                # from courses.services.lesson_actions_service.remove_lesson import remove_lesson
                # await remove_lesson(item["lesson_id"])

    await sync_to_async(mongo_repo.delete_document_by_id)("module_structures", module.structure_ids)

    await remove_data_from_structure(
        target_type="course",
        target_id=module.course_id,
        filter_data={"module_id": str(module.id)}
    )

    await sync_to_async(module.delete)()

    return success_response({"message": _("Module deleted successfully")})
