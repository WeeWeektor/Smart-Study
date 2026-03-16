from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from common.services import mongo_repo
from common.utils import success_response
from courses.models import Module
from courses.services.structure_course_module_action_service import remove_data_from_structure, \
    delete_files_from_supabase


async def remove_test(uuid_obj, test_type: str):
    from courses.services.test_actions_service import prepare_test_for_action
    test = await prepare_test_for_action(uuid_obj, test_type, action="delete")

    if test_type == 'module':
        module = await Module.objects.only("course_id").aget(pk=test.module_id)
        course_id = str(module.course_id)
    else:
        course_id = str(test.course_id)

    question_data = await sync_to_async(mongo_repo.get_document_by_id)("questions_data_for_test", str(test.test_data_ids))

    files_to_delete = []
    for question in question_data.get('questions', []):
        image_url = question.get('image_url')
        if image_url:
            files_to_delete.append(image_url)

    if files_to_delete:
        await delete_files_from_supabase(course_id, f"{test_type}-test", files_to_delete)

    if test_type in ("module", "course"):
        await remove_data_from_structure(
            target_type=test_type,
            target_id=str(test.module_id if test_type == "module" else test.course_id),
            filter_data={"test_id": str(test.id)}
        )

    await sync_to_async(mongo_repo.delete_document_by_id)("questions_data_for_test", str(test.test_data_ids))
    await sync_to_async(test.delete)()

    return success_response({"message": _(f"{test_type.capitalize()} test deleted successfully")})
