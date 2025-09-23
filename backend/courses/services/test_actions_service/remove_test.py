from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from common.services import mongo_repo
from common.utils import success_response


async def remove_test(uuid_obj, test_type: str):
    from courses.services.test_actions_service import prepare_test_for_action
    test = await prepare_test_for_action(uuid_obj, test_type, action="delete")

    await sync_to_async(mongo_repo.delete_document_by_id)("questions_data_for_test", str(test.test_data_ids))
    await sync_to_async(test.delete)()

    return success_response({"message": _(f"{test_type.capitalize()} test deleted successfully")})
