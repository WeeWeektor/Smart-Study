"""CourseAnnouncement
Клас: оголошення для курсу.

Поля:
- course: ForeignKey('Course') — пов'язаний курс, related_name='announcements'.
- title: CharField(max_length=200) — заголовок оголошення.
- content: TextField — текст оголошення.
- created_at: DateTimeField(auto_now_add=True) — час створення.
- is_important: BooleanField(default=False) — прапорець важливого оголошення.

Meta:
- ordering = ['-created_at'].
- verbose_name/verbose_name_plural.
- indexes: Index(fields=['course', '-created_at']), Index(fields=['is_important']).

Строкове представлення:
- "{course.title} - {title}".
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel


class CourseAnnouncement(BaseModel):
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='announcements',
        verbose_name=_("Course")
    )
    title = models.CharField(max_length=200, verbose_name=_("Announcement title"))
    content = models.TextField(verbose_name=_("Announcement content"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    is_important = models.BooleanField(default=False, verbose_name=_("Is important"))

    class Meta:
        db_table = "course_announcements"
        verbose_name = _("Course Announcement")
        verbose_name_plural = _("Course Announcements")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['course', '-created_at'], name="ix_announcement_course_created"),
            models.Index(fields=['is_important'], name="ix_announcement_important"),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"
