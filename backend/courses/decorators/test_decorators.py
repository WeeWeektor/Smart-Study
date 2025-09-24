import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from common.utils import error_response, validate_uuid
from courses.decorators import teacher_required
from courses.models import Test
from .validators import (
    validate_course_owner,
    validate_module_owner,
    validate_public_test_owner,
)


async def _check_test_permission(user, test_id=None, data=None):
    """
    Перевірка прав користувача:
    - public test → викладач
    - course/module test → викладач + власник курсу
    Для POST тесту data містить course_id/module_id/is_public.
    Для PATCH/DELETE test_id визначає тест.
    """
    if test_id is None:
        if not data:
            return False, _("No data provided for test creation.")

        if data.get("is_public", False):
            return True, None

        if data.get("course_id"):
            return await validate_course_owner(user, data["course_id"], "add test to")

        if data.get("module_id"):
            return await validate_module_owner(user, data["module_id"], "add test")

        return False, _("Cannot determine target course or module.")

    try:
        uuid_obj = validate_uuid(test_id)
        test = await sync_to_async(Test.objects.select_related("course", "module").get)(pk=uuid_obj)
    except ValidationError as e:
        return False, str(e)
    except Test.DoesNotExist:
        return False, _("Test not found.")

    if test.is_public:
        return await validate_public_test_owner(user, test.id, "modify")
    if test.course_id:
        return await validate_course_owner(user, test.course_id, "modify test in")
    if test.module_id:
        return await validate_module_owner(user, test.module_id, "modify test")

    return False, _("Test is not linked to course or module.")


def permission_test_required(func):
    """
    Універсальний декоратор для post, patch, delete.
    """

    @teacher_required
    async def wrapper(self, request, *args, **kwargs):
        test_id = kwargs.get("test_id")

        data = None
        if test_id is None:
            data = json.loads(request.POST.get("data", "{}"))

        has_perm, error_msg = await _check_test_permission(request.user, test_id=test_id, data=data)
        if not has_perm:
            return error_response(error_msg, status=403)

        return await func(self, request, *args, **kwargs)

    return wrapper
