from asgiref.sync import sync_to_async

from common.utils import validate_uuid
from courses.models import UserCourseEnrollment
from courses.serializers import UserCourseEnrollmentSerializer


async def get_course_enrollment_status(course_id, user_id):
    course_id = validate_uuid(course_id)
    user_id = validate_uuid(user_id)

    try:
        enrollment = await UserCourseEnrollment.objects.select_related('user', 'course') \
            .aget(course_id=course_id, user_id=user_id)

        data = await sync_to_async(lambda: UserCourseEnrollmentSerializer(enrollment).data)()
        return data

    except UserCourseEnrollment.DoesNotExist:
        return {
            "id": None,
            "progress": 0,
            "is_fully_completed": False,
            "is_failed": False,
            "certificate_url": None,
            "course_title": None,
            "course_description": None,
            "course_owner_id": None,
            "status": "not_started"
        }
    except Exception:
        return None
