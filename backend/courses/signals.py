from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import CourseReview, Course
from .task import train_course_recommendations


@receiver(post_save, sender=CourseReview)
def review_saved(sender, instance, **kwargs):
    """Оновлюємо CourseMeta після створення або оновлення відгуку"""
    if hasattr(instance.course, 'details'):
        instance.course.details.update_feedback_count_summary_and_rating()


@receiver(post_delete, sender=CourseReview)
def review_deleted(sender, instance, **kwargs):
    """Оновлюємо CourseMeta після видалення відгуку"""
    if hasattr(instance.course, 'details'):
        instance.course.details.update_feedback_count_summary_and_rating()


@receiver(post_save, sender=Course)
def trigger_ml_training_on_course_update(sender, instance, created, **kwargs):
    """
    Запускає перетренування моделі, якщо:
    1. Створено новий опублікований курс.
    2. Існуючий курс змінив статус на 'is_published=True'.
    """
    if instance.is_published:
        train_course_recommendations.delay()
