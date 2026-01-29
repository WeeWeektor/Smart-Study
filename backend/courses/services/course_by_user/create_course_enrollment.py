from common.utils import validate_uuid
from courses.models import UserCourseEnrollment, Course


async def create_course_enrollment(course_id, user_id):
    course_id = validate_uuid(course_id)
    user_id = validate_uuid(user_id)

    course = await Course.objects.aget(id=course_id)

    enrollment, created = await UserCourseEnrollment.objects.aget_or_create(
        user_id=user_id,
        course_id=course_id,
        defaults={
            'course_version': course.version
        }
    )

    if created:
        from .remove_course_from_wishlist import remove_course_from_wishlist
        await remove_course_from_wishlist(user_id, course_id)

    return enrollment, created
