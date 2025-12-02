import logging
import json
from typing import Union

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext

from common.utils import validate_uuid, error_response
from courses.models import Lesson
from courses.services.builder_json import build_lesson_json

logger = logging.getLogger(__name__)


async def get_lesson_by_id(lesson_id) -> Union[dict, list]:
    try:
        lesson_id = validate_uuid(lesson_id)

        lesson_data = await sync_to_async(lambda: Lesson.objects.get(id=lesson_id))() # TODO check if this correct work with return in browser
        print(lesson_data)
        return build_lesson_json(lesson_data) # TODO build lesson json such as in the test service
    except Lesson.DoesNotExist:
        return error_response(gettext("Lesson not found"), status=404)
    except ValidationError as e:
        return error_response(str(e), status=400)
    except Exception as e:
        logger.error(f"{gettext('Error receiving lesson')} ({lesson_id}): {str(e)}")
        return error_response(
            f"{gettext('Error receiving lesson')} ({lesson_id}): {str(e)})",
            status=500
        )
