"""CourseMeta
Клас: додаткові метадані курсу (структура, лічильники, рейтинг тощо).

Поля:
- course: OneToOneField('Course') — пов'язаний курс, related_name='details'.
- total_modules: PositiveIntegerField(default=0) — кількість модулів.
- total_lessons: PositiveIntegerField(default=0) — кількість уроків.
- total_tests: PositiveIntegerField(default=0) — кількість тестів.
- time_to_complete: DurationField(default=timedelta(0)) — очікуваний час для завершення.
- course_language: CharField(max_length=50, default='English') — мова курсу.
- rating: DecimalField — рейтинг з валідацією [0,5].
- level: CharField(choices=COURSE_LEVELS) — рівень курсу (індексоване).
- number_completed: PositiveIntegerField — кількість завершень.
- number_of_active: PositiveIntegerField — кількість активних.
- feedback_count: PositiveIntegerField — кількість відгуків.
- feedback: JSONField(default=dict) — агрегований фідбек.

Методи:
- update_counters(self) — агрегує enrollments курсу, оновлює number_of_active та number_completed і зберігає лише ці поля.

Meta:
- verbose_name/verbose_name_plural.
- indexes: course, level, -rating, -number_completed.

Строкове представлення:
- "CourseMeta - {course.title}" (локалізовано).
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Index, Q, Count, Avg
from django.utils.translation import gettext_lazy as _

from .base import BaseModel
from ..choices import LEVELS


class CourseMeta(BaseModel):
    course = models.OneToOneField('Course', on_delete=models.CASCADE, related_name='details', verbose_name=_("Course"))
    total_modules = models.PositiveIntegerField(default=0, verbose_name=_("Total modules"))
    total_lessons = models.PositiveIntegerField(default=0, verbose_name=_("Total lessons"))
    total_tests = models.PositiveIntegerField(default=0, verbose_name=_("Total tests"))
    time_to_complete = models.DurationField(verbose_name=_("Time to complete course"))
    course_language = models.CharField(max_length=50, default='English', verbose_name=_("Course language"))
    rating = models.DecimalField(
        default=0,
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name=_("Course rating")
    )
    level = models.CharField(max_length=100, db_index=True, verbose_name=_("Course level"), choices=LEVELS)
    number_completed = models.PositiveIntegerField(default=0, verbose_name=_("Count is completed course"))
    number_of_active = models.PositiveIntegerField(default=0, verbose_name=_("Count active course"))
    feedback_count = models.PositiveIntegerField(default=0, verbose_name=_("Review count"))
    feedback_summary = models.JSONField(default=dict, blank=True, verbose_name=_("Feedback summary"))

    def before_publish(self):
        """Метод який перед публікацією курсу з підраховує кількість модулів, уроків і тестів"""
        self.total_modules = self.course.modules.count()
        self.total_lessons = sum(module.lessons.count() for module in self.course.modules.all())
        self.total_tests = (
                sum(module.module_tests.count() for module in self.course.modules.all()) +
                self.course.course_tests.count()
        )
        self.save(update_fields=['total_modules', 'total_lessons', 'total_tests'])


    def update_counters(self):
        """Метод для автоматичного оновлення лічильників"""
        enrollments = self.course.enrollments.aggregate(
            active_count=Count('id', filter=Q(completed=False)),
            completed_count=Count('id', filter=Q(completed=True)),
        )

        self.number_of_active = enrollments['active_count'] or 0
        self.number_completed = enrollments['completed_count'] or 0

        self.save(update_fields=['number_of_active', 'number_completed'])


    def update_feedback_count_summary_and_rating(self):
        """Метод для оновлення кількості відгуків, їх зведення та рейтингу курсу"""
        reviews = self.course.reviews.all()

        stats = reviews.aggregate(
            avg_rating=Avg('rating'),
            count_reviews=Count('id'),
        )
        self.rating = stats['avg_rating'] or 0
        self.feedback_count = stats['count_reviews'] or 0

        summary = {}
        for r in range(1, 6):
            summary[str(r)] = reviews.filter(rating=r).count()
        self.feedback_summary = summary

        self.save(update_fields=['rating', 'feedback_count', 'feedback_summary'])


    def __str__(self):
        return f"{_('CourseMeta')} - {self.course.title}"


    class Meta:
        db_table = "course_meta"
        verbose_name = _("Course detail")
        verbose_name_plural = _("Course details")
        indexes = [
            Index(fields=['course'], name="ix_meta_course"),
            Index(fields=['level'], name="ix_meta_level"),
            Index(fields=['-rating'], name="ix_meta_rating_desc"),
            Index(fields=['-number_completed'], name="ix_meta_completed_desc"),
        ]
