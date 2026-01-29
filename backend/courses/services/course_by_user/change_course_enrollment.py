from datetime import timedelta

from django.utils import timezone

from common.utils import validate_uuid
from courses.models import UserCourseEnrollment, LessonProgress
from django.shortcuts import get_object_or_404

def update_enrollment_progress_sync(user_id,
                                    course_id,
                                    element_id,
                                    time_spent_seconds,
                                    is_completed,
                                    finished_course,
                                    element_type):
    user_id = validate_uuid(user_id)
    course_id = validate_uuid(course_id)
    element_id = validate_uuid(element_id) if element_id else None

    enrollment = get_object_or_404(UserCourseEnrollment, user_id=user_id, course_id=course_id)

    time_delta = timedelta(seconds=int(time_spent_seconds)) if time_spent_seconds else timedelta(0)

    if time_delta > timedelta(0):
        enrollment.time_spent += time_delta
        enrollment.save(update_fields=['time_spent'])

    if element_id and element_type == 'lesson':
        lesson_progress, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson_id=element_id)

        if time_delta > timedelta(0):
            lesson_progress.time_spent += time_delta

        if is_completed and not lesson_progress.completed_at:
            lesson_progress.completed_at = timezone.now()
            lesson_progress.completion_percentage = 100

        lesson_progress.save()

    if finished_course:
        enrollment.mark_as_completed()

    enrollment.calculate_progress()

    return {
        "progress": float(enrollment.progress),
        "is_completed": enrollment.completed,
        "time_spent": str(enrollment.time_spent),
        "element_id": element_id
    }
