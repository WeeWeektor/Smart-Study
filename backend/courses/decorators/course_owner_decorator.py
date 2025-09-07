from django.utils.translation import gettext as _

from common.utils import error_response
from courses.decorators import teacher_required


def owner_course_required(func):
    """Декоратор для перевірки, чи є користувач власником курсу (викладачем)"""

    @teacher_required
    async def wrapper(self, request, *args, **kwargs):
        course = self.get_object()
        if course.owner != request.user:
            return error_response(_("Only owner can make changes to courses."), status=403)
        return await func(self, request, *args, **kwargs)

    return wrapper
