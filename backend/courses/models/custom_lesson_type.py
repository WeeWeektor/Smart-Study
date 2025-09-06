"""CustomLessonType
Клас: налаштований тип уроку, створений користувачем.

Поля:
- name: CharField(max_length=100) — назва типу.
- description: TextField(max_length=500, blank=True, null=True).
- creator: ForeignKey(CustomUser), related_name='custom_lesson_types'.
- content_schema: JSONField(default=dict) — схема валідації контенту.
- is_public: BooleanField(default=False) — чи доступний іншим.
- is_active: BooleanField(default=True).
- created_at: DateTimeField(auto_now_add=True).
- usage_count: PositiveIntegerField(default=0) — лічильник використань.

Методи:
- increment_usage(self) — інкрементує usage_count і зберігає тільки поле usage_count.

Meta:
- constraints: UniqueConstraint(fields=['creator','name']) — унікальність назви в межах творця.
- indexes: creator, is_public, is_active, -usage_count.

Строкове представлення:
- "{name} ({creator.name} {creator.surname} - Email: {creator.email})"
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser
from .base import BaseModel


class CustomLessonType(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Lesson type name"))
    description = models.TextField(max_length=500, blank=True, null=True, verbose_name=_("Description"))
    creator = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='custom_lesson_types',
        verbose_name=_("Creator")
    )
    content_schema = models.JSONField(default=dict, blank=True, verbose_name=_("Content validation schema"))
    is_public = models.BooleanField(default=False, verbose_name=_("Is public type"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    usage_count = models.PositiveIntegerField(default=0, verbose_name=_("Usage count"))

    def increment_usage(self):
        """Збільшує лічильник використання"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

    class Meta:
        verbose_name = _("Custom Lesson Type")
        verbose_name_plural = _("Custom Lesson Types")
        constraints = [
            models.UniqueConstraint(fields=['creator', 'name'], name='unique_lesson_type_per_creator'),
        ]
        indexes = [
            models.Index(fields=['creator'], name="ix_custom_type_creator"),
            models.Index(fields=['is_public'], name="ix_custom_type_public"),
            models.Index(fields=['is_active'], name="ix_custom_type_active"),
            models.Index(fields=['-usage_count'], name="ix_custom_type_usage"),
        ]

    def __str__(self):
        return f"{self.name} ({self.creator.name} {self.creator.surname} - Email: {self.creator.email})"
