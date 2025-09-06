from django.utils.translation import gettext as _

from common.utils import error_response


def teacher_required(func):
    """Декоратор для перевірки, чи є користувач викладачем"""
    async def wrapper(self, request, *args, **kwargs):
        if getattr(request.user, 'role', None) != 'teacher':
            return error_response(_("Only teachers can make changes to courses."), status=403)
        return await func(self, request, *args, **kwargs)
    return wrapper
