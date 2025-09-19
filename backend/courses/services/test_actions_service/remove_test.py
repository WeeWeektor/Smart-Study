from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from common.services import mongo_repo
from common.utils import success_response
from courses.models import Test


async def remove_test(uuid_obj, test_type: str):
    strategies = {
        "module": lambda: Test.objects.select_related("module").get(pk=uuid_obj),
        "course": lambda: Test.objects.select_related("course").get(pk=uuid_obj),
        "public": lambda: Test.objects.select_related("owner").get(pk=uuid_obj),
    }

    test = await sync_to_async(strategies[test_type])()
    if not test:
        raise Test.DoesNotExist(_("Test not found"))

    if test_type == "public" and test.is_public:
        await sync_to_async(mongo_repo.delete_document_by_id)("questions_data_for_test", str(test.test_data_ids))

        await sync_to_async(test.delete)()
        return success_response({"message": _("Public test deleted successfully")})
