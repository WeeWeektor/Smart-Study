from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Index, Q
from django.utils.translation import gettext_lazy as _

from .base import BaseModel
from .module import Module
from ..choices import CATEGORY_LESSONS


class Lesson(BaseModel):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_("Module")
    )
    title = models.CharField(
        max_length=100,
        verbose_name=_("Lesson title")
    )
    description = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name=_("Lesson description")
    )
    content_type = models.CharField(
        max_length=50,
        choices=CATEGORY_LESSONS,
        default="text",
        verbose_name=_("Lesson content type")
    )
    content = models.TextField(
        max_length=7000,
        blank=True,
        verbose_name=_("Content (Markdown)")
    )
    order = models.PositiveIntegerField(
        verbose_name=_("Lesson order")
    )
    duration = models.DurationField(
        default=timedelta(0),
        verbose_name=_("Lesson duration")
    )

    def clean(self):
        super().clean()
        if self.content and len(self.content) > 7000:
            raise ValidationError({
                'content': _("Content length exceeds 7000 characters.")
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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
        ]
        indexes = [
            Index(fields=['module', 'title'], name="ix_lesson_module_title"),
            Index(fields=['module', 'order'], name="ix_lesson_module_order"),
            Index(fields=['content_type'], name="ix_lesson_content_type"),
        ]
