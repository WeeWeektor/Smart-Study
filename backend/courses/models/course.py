"""Course
Клас: основна модель курсу.

Поля:
- title: CharField(max_length=100) — назва курсу.
- description: TextField(max_length=1000).
- category: CharField(choices=CATEGORY_CHOICES, db_index=True).
- owner: ForeignKey(CustomUser), related_name='courses'.
- cover_image: URLField(blank=True, null=True).
- is_published: BooleanField(default=False, db_index=True).
- created_at: DateTimeField(auto_now_add=True, db_index=True).
- published_at: DateTimeField(blank=True, null=True).
- updated_at: DateTimeField(auto_now=True).
- version: PositiveIntegerField(default=1) — поточна версія курсу.

Методи:
- create_version_snapshot(self) — створює знімок поточного стану курсу та його зв'язаних модулів, уроків і тестів; серіалізує об'єкти через django.core.serializers.serialize і зберігає в CourseVersion; перед створенням видаляє попередні CourseVersion з таким course_id.
- update_version(self) — викликає create_version_snapshot(), інкрементує поле version і зберігає only version.
- publish(self) — якщо курс не опублікований, встановлює is_published=True, published_at=now і зберігає поля is_published та published_at.
- __str__ — "Course - {title}".

Meta:
- ordering = ['-created_at', 'id'].
- constraints:
  - UniqueConstraint(fields=['owner','title']) — унікальна назва курсу для власника.
  - CheckConstraint: якщо is_published=True тоді published_at не null.
- indexes: Index(fields=['category','is_published']), Index(fields=['owner','is_published']), Index(fields=['-created_at']).
"""

from django.core import serializers
from django.db import models
from django.db.models import Index, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser
from .base import BaseModel
from ..choices import CATEGORY_CHOICES


class Course(BaseModel):
    title = models.CharField(max_length=100, verbose_name=_("Course title"))
    description = models.TextField(max_length=1000, verbose_name=_("Course description"))
    category = models.CharField(max_length=100, db_index=True, verbose_name=_("Category"), choices=CATEGORY_CHOICES)
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name=_("Course owner")
    )
    cover_image = models.URLField(max_length=500, blank=True, null=True, verbose_name=_("Cover image URL"))
    is_published = models.BooleanField(default=False, db_index=True, verbose_name=_("Is published"))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("Created at"))
    published_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Published at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    version = models.PositiveIntegerField(default=1, verbose_name=_("Course version"))

    def create_version_snapshot(self):
        """Метод для створення знімка версії курсу"""
        from .course_version import CourseVersion

        CourseVersion.objects.filter(course_id=self.id).delete()

        course_data = {
            'course': serializers.serialize('json', [self]),
            'modules': [],
            'lessons': [],
            'tests': [],
        }

        for module in self.modules.all():
            course_data['modules'].append(serializers.serialize('json', [module]))

            for lesson in module.lessons.all():
                course_data['lessons'].append(serializers.serialize('json', [lesson]))

            for test in module.module_tests.all():
                course_data['tests'].append(serializers.serialize('json', [test]))

        for test in self.course_tests.all():
            course_data['tests'].append(serializers.serialize('json', [test]))

        if hasattr(self, 'details'):
            course_data['meta'] = serializers.serialize('json', [self.details])

        CourseVersion.objects.create(
            course_id=self.id,
            version_number=self.version,
            title=self.title,
            description=self.description,
            category=self.category,
            owner=self.owner,
            cover_image=self.cover_image,
            course_data=course_data
        )

    def update_version(self):
        """Оновлює версію курсу зі збереженням попередньої"""
        self.create_version_snapshot()
        self.version += 1
        self.save(update_fields=['version'])

    def publish(self):
        """Метод для публікації курсу з автоматичним встановленням часу"""
        if not self.is_published:
            self.is_published = True
            self.published_at = timezone.now()
            self.save(update_fields=['is_published', 'published_at'])

    def __str__(self):
        return f"{_("Course")} - {self.title}"

    class Meta:
        db_table = "courses"
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        ordering = ['-created_at', 'id']
        constraints = [
            models.UniqueConstraint(fields=['owner', 'title'], name='unique_course_title_per_owner'),
            models.CheckConstraint(
                name="course_published_requires_timestamp",
                check=(
                        Q(is_published=True, published_at__isnull=False) |
                        Q(is_published=False)
                ),
            ),
        ]
        indexes = [
            Index(fields=['category', 'is_published'], name="ix_course_category_published"),
            Index(fields=['owner', 'is_published'], name="ix_course_owner_published"),
            Index(fields=['-created_at'], name="ix_course_created_desc"),
        ]
