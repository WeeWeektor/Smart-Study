"""Lesson
Клас: урок у модулі.

Поля:
- module: ForeignKey('Module'), related_name='lessons'.
- title: CharField(max_length=100).
- description: TextField(max_length=1000, blank=True, null=True).
- content_type: CharField(choices=CATEGORY_LESSONS, default='text').
- custom_type: ForeignKey('CustomLessonType', on_delete=SET_NULL, blank=True, null=True, related_name='lessons').
- resources: JSONField(default=list) — додаткові ресурси.
- content: JSONField(default=dict) — дані контенту.
- order: PositiveIntegerField — позиція в модулі.
- duration: DurationField(default=timedelta(0)) — тривалість уроку.

Методи:
- save(self, *args, **kwargs) — після створення (is_new) якщо вказано custom_type викликає custom_type.increment_usage().
- __str__ — "Lesson - {title} ({module.title})".

Meta:
- ordering = ['order', 'id'].
- constraints:
  - UniqueConstraint(module, title)
  - UniqueConstraint(module, order)
  - CheckConstraint order > 0
  - CheckConstraint: якщо content_type='custom' то custom_type не null; і навпаки
- indexes: module+title, module+order, content_type.
"""

from datetime import timedelta

from django.db import models
from django.db.models import Index, Q
from django.utils.translation import gettext_lazy as _

from .base import BaseModel
from ..choices import CATEGORY_LESSONS


class Lesson(BaseModel):
    module = models.ForeignKey('Module', on_delete=models.CASCADE, related_name='lessons', verbose_name=_("Module"))
    title = models.CharField(max_length=100, verbose_name=_("Lesson title"))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Lesson description"))
    content_type = models.CharField(
        max_length=50,
        choices=CATEGORY_LESSONS,
        default="text",
        verbose_name=_("Lesson content type")
    )
    custom_type = models.ForeignKey(
        'CustomLessonType',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='lessons',
        verbose_name=_("Custom lesson type")
    )
    resources = models.JSONField(default=list, blank=True, verbose_name=_("Resources"))
    content = models.JSONField(default=dict, blank=True, verbose_name=_("Content data"))
    order = models.PositiveIntegerField(verbose_name=_("Lesson order"))
    duration = models.DurationField(default=timedelta(0), verbose_name=_("Lesson duration"))

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.custom_type:
            self.custom_type.increment_usage()

    def __str__(self):
        return f"{_('Lesson')} - {self.title} ({self.module.title})"

    class Meta:
        db_table = "lessons"
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['module', 'title'], name='unique_lesson_title_per_module'),
            models.UniqueConstraint(fields=['module', 'order'], name='unique_lesson_order_per_module'),
            models.CheckConstraint(name="lesson_order_positive", check=Q(order__gt=0)),
            models.CheckConstraint(
                name="lesson_custom_type_valid",
                check=(
                        Q(content_type='custom', custom_type__isnull=False) |
                        Q(~Q(content_type='custom'), custom_type__isnull=True)
                ),
            ),
        ]
        indexes = [
            Index(fields=['module', 'title'], name="ix_lesson_module_title"),
            Index(fields=['module', 'order'], name="ix_lesson_module_order"),
            Index(fields=['content_type'], name="ix_lesson_content_type"),
        ]
