from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

from common.utils import error_response, validate_uuid
from courses.models import Test
from courses.decorators import teacher_required
from django.core.exceptions import ValidationError


def owner_public_test_required(func):
    """Декоратор для перевірки, чи є користувач власником публічного тесту (викладачем)"""

    @teacher_required
    async def wrapper(self, request, *args, **kwargs):
        test_id = kwargs.get("test_id")
        if not test_id:
            return error_response(_("Test ID not provided."), status=400)

        try:
            uuid_obj = validate_uuid(test_id)
            test = await sync_to_async(Test.objects.only("owner_id").get)(pk=uuid_obj)
        except Test.DoesNotExist:
            return error_response(_("Test not found."), status=404)
        except ValidationError as e:
            return error_response(str(e), status=400)

        if test.owner_id != request.user.id:
            return error_response(_("Only owner can make changes to test."), status=403)

        return await func(self, request, *args, **kwargs)

    return wrapper
