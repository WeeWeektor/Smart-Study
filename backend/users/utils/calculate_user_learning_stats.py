from asgiref.sync import sync_to_async
from django.db.models import Count, Q

from courses.models import UserCourseEnrollment, TestAttempt, LessonProgress, Certificate


async def calculate_user_learning_stats(user_id):
    def get_stats():
        enroll_stats = UserCourseEnrollment.objects.filter(user_id=user_id).aggregate(
            с_completed=Count('id', filter=Q(completed=True)),
            с_in_progress=Count('id', filter=Q(completed=False))
        )

        passed_tests_count = TestAttempt.objects.filter(
            user_id=user_id,
            passed=True
        ).values('test').distinct().count()

        completed_topics_count = LessonProgress.objects.filter(
            enrollment__user_id=user_id,
            completed_at__isnull=False
        ).count()

        certificates_count = Certificate.objects.filter(
            user_id=user_id,
            is_valid=True
        ).count()

        return {
            "coursesCompleted": enroll_stats['с_completed'],
            "coursesInProgress": enroll_stats['с_in_progress'],
            "totalTests": passed_tests_count,
            "completedTopics": completed_topics_count,
            "certificates": certificates_count,
        }

    return await sync_to_async(get_stats, thread_sensitive=True)()
