"""Module
Клас: модуль у курсі.

Поля:
- course: ForeignKey(Course), related_name='modules'.
- title: CharField(max_length=100).
- description: TextField(max_length=1000, blank=True, null=True).
- order: PositiveIntegerField — порядок модуля у курсі.
- module_structure: JSONField(default=list) — структура модуля.

Методи:
- __str__ — "Module - {title} ({course.title})".

Meta:
- ordering = ['order', 'id'].
- constraints:
  - UniqueConstraint(course, title)
  - UniqueConstraint(course, order)
  - CheckConstraint order > 0
- indexes: course+title, course+order.
"""

from django.db import models
from django.db.models import Index, Q
from django.utils.translation import gettext_lazy as _

from .base import BaseModel
from .course import Course


class Module(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name=_("Course"))
    title = models.CharField(max_length=100, verbose_name=_("Module title"))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_("Module description"))
    order = models.PositiveIntegerField(verbose_name=_("Module order"))
    # module Structure

    def __str__(self):
        return f"{_('Module')} - {self.title} ({self.course.title})"

    class Meta:
        db_table = "modules"
        verbose_name = _("Module")
        verbose_name_plural = _("Modules")
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['course', 'title'], name='unique_module_title_per_course'),
            models.UniqueConstraint(fields=['course', 'order'], name='unique_module_order_per_course'),
            models.CheckConstraint(name="module_order_positive", check=Q(order__gt=0)),
        ]
        indexes = [
            Index(fields=['course', 'title'], name="ix_module_course_title"),
            Index(fields=['course', 'order'], name="ix_module_course_order"),
        ]
