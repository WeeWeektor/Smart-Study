from common.utils import validate_uuid
from courses.models import Course, UserCourseEnrollment
from courses.utils import generate_course_json_with_details_and_owner


async def get_courses_by_user(user_id):
    user_id = validate_uuid(user_id)

    wishlist_courses_queryset = (Course.objects
                                 .filter(wishlisted_by__user_id=user_id))

    course_enrolled_queryset = (UserCourseEnrollment.objects
                                .filter(user_id=user_id, completed=False)
                                .select_related('course'))

    course_completed_queryset = (UserCourseEnrollment.objects
                                 .filter(user_id=user_id, completed=True)
                                 .select_related('course'))

    wishlist_courses = [course async for course in wishlist_courses_queryset]
    in_wishlist = await generate_course_json_with_details_and_owner(wishlist_courses)

    enrolled_enrollments = [e async for e in course_enrolled_queryset]
    enrolled_courses = [e.course for e in enrolled_enrollments]
    is_enrolled_base = await generate_course_json_with_details_and_owner(enrolled_courses)
    is_enrolled = _inject_enrollment_data(is_enrolled_base, enrolled_enrollments)

    completed_enrollments = [e async for e in course_completed_queryset]
    completed_courses = [e.course for e in completed_enrollments]
    is_completed_base = await generate_course_json_with_details_and_owner(completed_courses)
    is_completed = _inject_enrollment_data(is_completed_base, completed_enrollments)

    return in_wishlist, is_enrolled, is_completed


def _inject_enrollment_data(courses_json: list, enrollments: list) -> list:
    enrollment_map = {str(e.course.id): e for e in enrollments}

    for item in courses_json:
        course_data = item.get('course')
        if not course_data:
            continue

        course_id = str(course_data.get('id'))
        enrollment = enrollment_map.get(course_id)

        if enrollment:
            course_data['user_status'] = {
                'progress': float(enrollment.progress),
                'is_completed': enrollment.completed,
                'enrolled_at': enrollment.enrolled_at,
                'completed_at': enrollment.completed_at,
            }

    return courses_json
