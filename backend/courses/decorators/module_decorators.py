import json

from django.utils.translation import gettext as _

from common.utils import error_response
from courses.decorators import teacher_required
from .validators import validate_course_owner, validate_module_permission


def permission_module_required(func):
    """
    Декоратор для post, patch, delete для module.
    Перевіряє чи користувач є викладачем, власником курсу до якого належить модуль і чи курс не опублікований.
    """

    @teacher_required
    async def wrapper(self, request, *args, **kwargs):
        module_id = kwargs.get("module_id")

        if request.method.lower() == "post":
            data = json.loads(request.POST.get("data", "{}"))
            course_id = data.get("course_id")
            if not course_id:
                return error_response(_("Course ID not provided for module creation."), status=400)

            has_perm, error_msg = await validate_course_owner(
                request.user, course_id, "create module", check_published=True
            )
        else:
            if not module_id:
                return error_response(_("Module ID not provided."), status=400)

            has_perm, error_msg = await validate_module_permission(
                request.user, module_id, "modify/delete module"
            )

        if not has_perm:
            return error_response(error_msg, status=403)

        return await func(self, request, *args, **kwargs)

    return wrapper
