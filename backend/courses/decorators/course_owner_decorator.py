from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

from common.utils import error_response, validate_uuid
from courses.models import Course
from courses.decorators import teacher_required
from django.core.exceptions import ValidationError


def owner_course_required(func):
    """Декоратор для перевірки, чи є користувач власником курсу (викладачем)"""

    @teacher_required
    async def wrapper(self, request, *args, **kwargs):
        course_id = kwargs.get("course_id")
        if not course_id:
            return error_response(_("Course ID not provided."), status=400)

        try:
            uuid_obj = validate_uuid(course_id)
            course = await sync_to_async(Course.objects.only("owner_id").get)(pk=uuid_obj)
        except Course.DoesNotExist:
            return error_response(_("Course not found."), status=404)
        except ValidationError as e:
            return error_response(str(e), status=400)

        if course.owner_id != request.user.id:
            return error_response(_("Only owner can make changes to courses."), status=403)

        return await func(self, request, *args, **kwargs)

    return wrapper
