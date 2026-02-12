from typing import List, Dict, Any

from django.db.models import F

from courses.models import Course


class CourseDBService:
    @staticmethod
    def get_training_data() -> List[Dict[str, Any]]:
        """Отримує "сирі" дані для тренування моделі."""
        courses = (Course.objects
                   .filter(is_published=True)
                   .select_related('details')
                   .values('id', 'title', 'description', 'details__level')
                   )
        return list(courses)

    @staticmethod
    def get_popular_courses_ids(limit: int) -> List[int]:
        """Повертає ID популярних курсів (Cold Start)."""
        print("Using Cold Start (Popular Courses)")
        popular_ids = (
            Course.objects
            .filter(is_published=True)
            .select_related('details')
            .annotate(
                total_students=(F('details__number_completed') + F('details__number_of_active'))
            )
            .order_by('-total_students', '-details__rating', '-published_at')
            .values_list('id', flat=True)[:limit]
        )
        return list(popular_ids)
