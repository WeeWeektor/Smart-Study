from django.core.exceptions import ObjectDoesNotExist

from common.utils import validate_uuid
from courses.models import UserCourseEnrollment, LessonProgress, TestAttempt


async def get_course_with_details_enrollment(course_id, user_id, course_data):
    course_id = validate_uuid(course_id)
    user_id = validate_uuid(user_id)

    try:
        try:
            enrollment = await UserCourseEnrollment.objects.aget(user_id=user_id, course_id=course_id)
        except ObjectDoesNotExist:
            return course_data

        lesson_progresses_list = [
            lp async for lp in LessonProgress.objects.filter(enrollment=enrollment)
        ]

        test_attempts_list = [
            ta async for ta in TestAttempt.objects.filter(enrollment=enrollment)
        ]

        last_element_id, last_element_type = _get_last_visited_element(lesson_progresses_list, test_attempts_list)

        serialized_lessons = [
            {
                'lesson_id': str(lp.lesson_id),
                'completed_at': lp.completed_at,
                'is_completed': lp.completed_at is not None,
            }
            for lp in lesson_progresses_list
        ]

        serialized_tests = [
            {
                'test_id': str(ta.test_id),
                'score': ta.score,
                'passed': ta.passed,
                'attempt_number': ta.attempt_number
            }
            for ta in test_attempts_list
        ]

        course_data['user_status'] = {
            'progress': float(enrollment.progress),
            'is_completed': enrollment.completed,
            'enrolled_at': enrollment.enrolled_at,
            'completed_at': enrollment.completed_at,
            'time_spent': str(enrollment.time_spent) if enrollment.time_spent else None,
            'last_visited_element_id': last_element_id,
            'last_visited_element_type': last_element_type,
            'lesson_progresses': serialized_lessons,
            'test_attempts': serialized_tests,
            'completed_elements': [
                                      str(lp.lesson_id) for lp in lesson_progresses_list if lp.completed_at
                                  ] + [
                                      str(ta.test_id) for ta in test_attempts_list if ta.passed
                                  ]
        }

        return course_data
    except Exception as e:
        print(f"Error in get_course_with_details_enrollment: {e}")
        return course_data


def _get_last_visited_element(lesson_progresses_list, test_attempts_list):
    last_element_id = None
    last_element_type = None
    last_timestamp = None

    for lp in lesson_progresses_list:
        ts = getattr(lp, 'updated_at', getattr(lp, 'completed_at', None))
        if ts and (last_timestamp is None or ts > last_timestamp):
            last_timestamp = ts
            last_element_id = str(lp.lesson_id)
            last_element_type = 'lesson'

    for ta in test_attempts_list:
        ts = getattr(ta, 'completed_at', getattr(ta, 'started_at', None))
        if ts and (last_timestamp is None or ts > last_timestamp):
            last_timestamp = ts
            last_element_id = str(ta.test_id)
            last_element_type = 'test'

    return last_element_id, last_element_type
