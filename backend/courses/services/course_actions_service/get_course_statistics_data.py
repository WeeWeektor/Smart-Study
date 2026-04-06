from django.db.models import Count, Q, Avg, Prefetch

from courses.models import Course, UserCourseEnrollment


def get_course_statistics_data(course_id):
    """
    Отримує курс з агрегованою статистикою одним запитом.
    """
    students_prefetch = Prefetch(
        'enrollments',
        queryset=UserCourseEnrollment.objects.select_related('user').order_by('-enrolled_at'),
        to_attr='prefetched_students'
    )

    course = Course.objects.annotate(
        stat_total_students=Count('enrollments', distinct=True),
        stat_in_progress=Count('enrollments', filter=Q(enrollments__completed=False), distinct=True),
        stat_completed=Count('enrollments', filter=Q(enrollments__completed=True), distinct=True),
        stat_success=Count('enrollments', filter=Q(enrollments__completed=True, enrollments__progress=100),
                           distinct=True),
        stat_failed=Count('enrollments', filter=Q(enrollments__completed=True) & ~Q(enrollments__progress=100),
                          distinct=True),
        stat_avg_rating=Avg('reviews__rating'),
        stat_total_reviews=Count('reviews', distinct=True)
    ).prefetch_related(students_prefetch).get(id=course_id)

    return course
