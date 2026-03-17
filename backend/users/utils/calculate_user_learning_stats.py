from asgiref.sync import sync_to_async
from django.db.models import Count, Q

from courses.models import TestAttempt, LessonProgress, UserCourseEnrollment, Certificate


async def calculate_user_learning_stats(user_id):
    enrollments_qs = UserCourseEnrollment.objects.filter(user_id=user_id)
    courses_stats = await sync_to_async(lambda: enrollments_qs.aggregate(
        с_completed=Count('id', filter=Q(completed=True)),
        с_in_progress=Count('id', filter=Q(completed=False))
    ))()

    passed_tests_count = await sync_to_async(
        lambda: TestAttempt.objects.filter(user_id=user_id, passed=True)
        .values('test_id')
        .distinct()
        .count()
    )()

    completed_topics_count = await sync_to_async(
        lambda: LessonProgress.objects.filter(
            enrollment__user_id=user_id,
            completed_at__isnull=False
        ).count()
    )()

    certificates_count = await sync_to_async(
        lambda: Certificate.objects.filter(user_id=user_id, is_valid=True).count()
    )()

    return {
        "coursesCompleted": courses_stats['с_completed'],
        "coursesInProgress": courses_stats['с_in_progress'],
        "totalTests": passed_tests_count,
        "completedTopics": completed_topics_count,
        "certificates": certificates_count,
    }
