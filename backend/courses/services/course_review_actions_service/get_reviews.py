import logging

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext

from common.utils import error_response, validate_uuid
from courses.models import CourseReview
from courses.services.builder_json import build_course_review_json

logger = logging.getLogger(__name__)


def _get_reviews_from_db(course_id):
    return list(
        CourseReview.objects
        .filter(course_id=course_id)
        .select_related('user', 'user__profile')
        .order_by('-created_at')
    )


async def get_course_review(course_id):
    try:
        valid_course_id = validate_uuid(course_id)

        reviews = await sync_to_async(_get_reviews_from_db)(valid_course_id)

        return [build_course_review_json(r) for r in reviews]

    except ValidationError as e:
        return error_response(str(e), status=400)

    except Exception as e:
        logger.error(f"{gettext('Error receiving review of courses')} ({course_id}): {str(e)}")
        return error_response(
            f"{gettext('Error receiving review of courses')}: {str(e)}",
            status=500
        )
