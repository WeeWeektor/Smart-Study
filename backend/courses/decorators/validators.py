from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from common.utils import validate_uuid
from courses.models import Module, Course, Test


async def validate_course_owner(user, course_id, action_msg, check_published=False):
    """Перевіряє чи user є власником курсу. Додатково перевірити is_published."""
    try:
        uuid_obj = validate_uuid(course_id)
        fields = ["owner_id"]
        if check_published:
            fields.append("is_published")
        course = await sync_to_async(Course.objects.only(*fields).get)(pk=uuid_obj)
    except Course.DoesNotExist:
        return False, _("Course not found.")
    except ValidationError as e:
        return False, str(e)

    if course.owner_id != user.id:
        return False, _(f"Only owner can {action_msg} this course.")
    if check_published and getattr(course, "is_published", False):
        return False, _("Cannot modify a published course.")
    return True, None


async def validate_module_owner(user, module_id, action_msg):
    """Перевіряє чи user є власником курсу, до якого належить модуль"""
    try:
        uuid_obj = validate_uuid(module_id)
        module = await sync_to_async(
            Module.objects.select_related("course").only("course__owner_id").get
        )(pk=uuid_obj)
    except Module.DoesNotExist:
        return False, _("Module not found.")
    except ValidationError as e:
        return False, str(e)

    if module.course.owner_id != user.id:
        return False, _(f"Only owner of module's course can {action_msg}.")
    return True, None


async def validate_module_permission(user, module_id, action_msg):
    """Перевіряє чи user є власником курсу, до якого належить модуль, і курс не опублікований."""
    try:
        uuid_obj = validate_uuid(module_id)
        module = await sync_to_async(
            Module.objects.select_related("course").only("course__owner_id", "course__is_published").get
        )(pk=uuid_obj)
    except Module.DoesNotExist:
        return False, _("Module not found.")
    except ValidationError as e:
        return False, str(e)

    if module.course.owner_id != user.id:
        return False, _(f"Only course owner can {action_msg}.")
    if module.course.is_published:
        return False, _("Cannot modify modules of a published course.")
    return True, None


async def validate_public_test_owner(user, test_id, action_msg):
    """Перевіряє чи user є власником public тесту"""
    try:
        uuid_obj = validate_uuid(test_id)
        test = await sync_to_async(Test.objects.only("owner_id").get)(pk=uuid_obj)
    except Test.DoesNotExist:
        return False, _("Test not found.")
    except ValidationError as e:
        return False, str(e)

    if test.owner_id != user.id:
        return False, _(f"Only owner can {action_msg} this test.")
    return True, None
