from django.utils.translation import gettext as _

from common.utils import error_response
from courses.decorators import teacher_required
from .validators import validate_course_owner


def owner_course_required(func):
    """Декоратор для перевірки, чи є користувач власником курсу (викладачем)"""

    @teacher_required
    async def wrapper(self, request, *args, **kwargs):
        course_id = kwargs.get("course_id")
        if not course_id:
            return error_response(_("Course ID not provided."), status=400)

        has_perm, error_msg = await validate_course_owner(request.user, course_id, "make changes to")
        if not has_perm:
            return error_response(error_msg, status=403)

        return await func(self, request, *args, **kwargs)

    return wrapper
