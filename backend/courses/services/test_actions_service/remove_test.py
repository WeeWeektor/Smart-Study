from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from common.services import mongo_repo
from common.utils import success_response, error_response
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

    data = {}
    if test_type == "course" and test.course_id:
        data["course_id"] = str(test.course_id)
    elif test_type == "module" and test.module_id:
        data["module_id"] = str(test.module_id)
    elif test_type == "public" and test.owner:
        data["owner"] = test.owner
    else:
        return error_response(_("Invalid test type"), status=400)

    from courses.services.test_actions_service import validate_test_editable
    error = await validate_test_editable(test_type, data, action="delete")
    if error:
        return error

    from courses.services.test_actions_service import cache_invalidators
    await sync_to_async(
        cache_invalidators(test_type, test, data["owner"] if "owner" in data else None),
        thread_sensitive=True
    )()

    msg = test_type.capitalize()
    return await _delete_test_by_id(test, msg)


async def _delete_test_by_id(test, msg: str):
    await sync_to_async(mongo_repo.delete_document_by_id)("questions_data_for_test", str(test.test_data_ids))
    await sync_to_async(test.delete)()
    return success_response({"message": _(f"{msg} test deleted successfully")})
