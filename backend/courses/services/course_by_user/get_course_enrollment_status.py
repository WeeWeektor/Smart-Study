from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from common.utils import validate_uuid, error_response
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
        return error_response(_("Enrollment not found"), status=404)
    except Exception as e:
        return error_response(_(f"Error checking status: {str(e)}"), status=500)
