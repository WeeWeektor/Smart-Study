from asgiref.sync import sync_to_async
from common.utils import validate_uuid
from courses.models import Module, Course
from django.utils.translation import gettext as _


async def get_structure_ids_obj(target_type: str, target_id: str):
    """
    Повертає об'єкт Django з полем structure_ids для course або module.

    :param target_type: 'course' або 'module'
    :param target_id: UUID об'єкта
    :return: об'єкт Django з полем structure_ids
    """
    uuid_obj = validate_uuid(target_id)

    if target_type == "course":
        return await sync_to_async(Course.objects.only("structure_ids").get)(pk=uuid_obj)
    elif target_type == "module":
        return await sync_to_async(Module.objects.only("structure_ids").get)(pk=uuid_obj)
    else:
        raise ValueError(_("target_type must be 'course' or 'module'"))
