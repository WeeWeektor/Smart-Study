"""LessonProgress
Клас: прогрес по конкретному уроку для enrollment.

Поля:
- enrollment: ForeignKey('UserCourseEnrollment'), related_name='lesson_progresses'.
- lesson: ForeignKey('Lesson'), related_name='progresses'.
- started_at: DateTimeField(auto_now_add=True).
- completed_at: DateTimeField(null=True, blank=True).
- time_spent: DurationField(default=timedelta(0)).
- completion_percentage: PositiveIntegerField(default=0).
- notes: TextField(blank=True).

Meta:
- constraints: UniqueConstraint(fields=['enrollment','lesson']) — одна запис прогресу на комбінацію.
- indexes: Index(enrollment, lesson), Index(completed_at).

Строкове представлення:
- "{lesson.title} - {enrollment.user.email}"
"""

from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel


class LessonProgress(BaseModel):
    enrollment = models.ForeignKey(
        'UserCourseEnrollment',
        on_delete=models.CASCADE,
        related_name='lesson_progresses',
        verbose_name=_("Enrollment"),
    )
    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.CASCADE,
        related_name='progresses',
        verbose_name=_("Lesson"),
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Started at"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed at"))
    time_spent = models.DurationField(default=timedelta(0), verbose_name=_("Time spent"))
    completion_percentage = models.PositiveIntegerField(default=0, verbose_name=_("Completion percentage"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Lesson Progress")
        verbose_name_plural = _("Lesson Progresses")
        constraints = [
            models.UniqueConstraint(
                fields=['enrollment', 'lesson'],
                name='unique_lesson_progress_per_enrollment'
            ),
        ]
        indexes = [
            models.Index(fields=['enrollment', 'lesson'], name="ix_progress_enrollment_lesson"),
            models.Index(fields=['completed_at'], name="ix_progress_completed_at"),
        ]

    def __str__(self):
        return f"{self.lesson.title} - {self.enrollment.user.email}"
