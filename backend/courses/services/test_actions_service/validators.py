from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from common.utils import validate_uuid, error_response
from courses.models import Course, Module


async def _get_course_by_test_type(test_type: str, data: dict):
    """
     Витягує курс за test_type (course/module).
     Якщо test_type = course -> дістає курс напряму
     Якщо test_type = module -> дістає курс через модуль
     """
    if test_type == "course":
        course_id = validate_uuid(data.get("course_id"))
        return await sync_to_async(Course.objects.only("is_published", "version").get)(pk=course_id)

    if test_type == "module":
        module_id = validate_uuid(data.get("module_id"))
        module = await sync_to_async(Module.objects
                                     .select_related("course")
                                     .only("course__is_published", "course__version")
                                     .get
                                     )(pk=module_id)
        return module.course

    return None


async def validate_test_editable(test_type: str, data: dict, action: str):
    """
        Перевіряє чи можна додати/редагувати/видаляти тест для курсу/модуля.
    """
    course = await _get_course_by_test_type(test_type, data)
    if not course:
        return None

    if course and course.is_published:
        return error_response(message=_("Cannot add/delete/edit test in a published course"), status=400)

    if (action == "delete" or action == "edit") and course.version != 1:
        return error_response(
            _("This test cannot be deleted/edited because it is part of a course version"),
            status=400
        )

    return None
