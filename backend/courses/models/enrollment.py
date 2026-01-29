"""UserCourseEnrollment
Клас: запис про запис користувача на курс (enrollment).

Поля:
- user: ForeignKey(CustomUser), related_name='enrollments'.
- course: ForeignKey(Course), related_name='enrollments'.
- course_version: PositiveIntegerField — версія курсу при записі.
- enrolled_at: DateTimeField(auto_now_add=True, db_index=True).
- progress: DecimalField(max_digits=5, decimal_places=2, default=0) — від 0 до 100.
- module_progress: JSONField(default=dict) — прогрес по модулях.
- lesson_progress: JSONField(default=dict) — прогрес по урокам.
- completed: BooleanField(default=False, db_index=True).
- completed_at: DateTimeField(null=True, blank=True).
- time_spent: DurationField(default=timedelta(0)).

Методи:
- save(self, *args, **kwargs) — якщо course_version не вказаний, встановлює поточну course.version перед збереженням.
- calculate_progress(self) — обчислює прогрес як (завершені уроки / total_lessons) * 100; встановлює completed і completed_at при досягненні >=100 та зберігає відповідні поля.
- mark_as_completed(self) — вручну відмічає як завершений, ставить completed_at = now, progress = 100, зберігає поля; якщо існують details курсу, викликає details.update_counters().

Meta:
- constraints: UniqueConstraint(fields=['user','course']); CheckConstraint щоб completed=True вимагало completed_at не null.
- indexes: user+completed, course+completed, enrolled_at, progress, course_version.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Index, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser
from .base import BaseModel
from .course import Course

User = get_user_model()


class UserCourseEnrollment(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments', verbose_name=_('User'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name=_('Course'))
    course_version = models.PositiveIntegerField(verbose_name=_('Course version at enrollment'))
    enrolled_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('Enrolled at'))
    progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Progress'),
    )
    completed = models.BooleanField(default=False, db_index=True, verbose_name=_('Completed'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed at'))
    time_spent = models.DurationField(default=timedelta(0), verbose_name=_('Time spent'))

    def save(self, *args, **kwargs):
        if not self.course_version:
            self.course_version = self.course.version
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name} {self.user.surname} - {self.course.title} v{self.course_version}"

    def calculate_progress(self):
        """Метод для обчислення прогресу користувача по курсу"""
        total_lessons = getattr(self.course.details, 'total_lessons', 0)
        total_tests = getattr(self.course.details, 'total_tests', 0)
        total_items = total_lessons + total_tests

        if total_items == 0:
            self.progress = 0
        else:
            completed_lessons_count = self.lesson_progresses.filter(
                completed_at__isnull=False
            ).count()
            passed_tests_count = self.test_attempts.filter(
                passed=True
            ).values('test').distinct().count()

            self.progress = ((completed_lessons_count + passed_tests_count) / total_items) * 100

        if self.progress >= 100 and not self.completed:
            self.completed = True
            self.completed_at = timezone.now()

        self.save(update_fields=['progress', 'completed', 'completed_at'])

    def mark_as_completed(self):
        """Метод для позначення курсу як завершеного"""
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.progress = 100
            self.save(update_fields=['completed', 'completed_at', 'progress'])

            if hasattr(self.course, 'details'):
                self.course.details.update_counters()

    class Meta:
        db_table = "user_course_enrollments"
        verbose_name = _('User Course Enrollment')
        verbose_name_plural = _('User Course Enrollments')
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course_enrollment'),
            models.CheckConstraint(
                name='enrollment_completed_requires_timestamp',
                check=Q(completed=False) | Q(completed=True, completed_at__isnull=False),
            ),
        ]
        indexes = [
            Index(fields=['user', 'completed'], name="ix_enrollment_user_completed"),
            Index(fields=['course', 'completed'], name="ix_enrollment_course_completed"),
            Index(fields=['enrolled_at'], name="ix_enrollment_enrolled_at"),
            Index(fields=['progress'], name="ix_enrollment_progress"),
            Index(fields=['course_version'], name="ix_enrollment_course_version"),
        ]
