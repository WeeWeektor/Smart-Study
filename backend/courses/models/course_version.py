"""CourseVersion
Клас: знімок версії курсу (історія змін).

Поля:
- course_id: UUIDField — оригінальний ID курсу.
- version_number: PositiveIntegerField — номер версії.
- title: CharField — назва на момент знімка.
- description: TextField — опис.
- category: CharField(choices=CATEGORY_CHOICES).
- owner: ForeignKey(CustomUser) — власник на момент знімка.
- cover_image: URLField(blank=True, null=True).
- course_data: JSONField — серіалізований знімок курсу (курси, модулі, уроки, тести, meta).
- created_at: DateTimeField(auto_now_add=True).

Методи:
- __str__ — повертає "Course - {title} v{version_number}".

Meta:
- ordering = ['-version_number'].
- constraints: UniqueConstraint(fields=['course_id','version_number']).
- indexes: Index(fields=['course_id','version_number']).
"""

from django.db import models
from django.db.models import Index
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser
from .base import BaseModel
from ..choices import CATEGORY_CHOICES


class CourseVersion(BaseModel):
    course_id = models.UUIDField(verbose_name=_("Original course ID"))
    version_number = models.PositiveIntegerField(verbose_name=_("Version number"))
    title = models.CharField(max_length=100, verbose_name=_("Course title"))
    description = models.TextField(max_length=1000, verbose_name=_("Course description"))
    category = models.CharField(max_length=100, verbose_name=_("Category"), choices=CATEGORY_CHOICES)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_("Course owner"))
    cover_image = models.URLField(max_length=500, blank=True, null=True, verbose_name=_("Cover image URL"))
    course_data = models.JSONField(verbose_name=_("Course snapshot data"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Version created at"))

    class Meta:
        db_table = "course_versions"
        verbose_name = _("Course Version")
        verbose_name_plural = _("Course Versions")
        ordering = ['-version_number']
        constraints = [
            models.UniqueConstraint(fields=['course_id', 'version_number'], name='unique_course_version'),
        ]
        indexes = [
            Index(fields=['course_id', 'version_number'], name="ix_version_course_number"),
        ]

    def __str__(self):
        return f"{_("Course")} - {self.title} v{self.version_number}"
