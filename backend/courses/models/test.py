"""Test
Клас: тест, прив'язаний до курсу або модуля, або публічний.

Поля:
- course: ForeignKey(Course, blank=True, null=True, related_name='course_tests').
- module: ForeignKey(Module, blank=True, null=True, related_name='module_tests').
- title: CharField(max_length=100).
- description: TextField(max_length=500, blank=True, null=True).
- time_limit: PositiveIntegerField(default=0) — хвилини.
- count_attempts: PositiveIntegerField(default=0) — 0 = необмежено.
- pass_score: FloatField(default=0.0) — відсоток проходження.
- randomize_questions: BooleanField(default=False).
- show_correct_answers: BooleanField(default=True).
- test_data_ids: JSONField(default=list) — ідентифікатори питань (Mongo).
- order: PositiveIntegerField.
- is_public: BooleanField(default=False, db_index=True).

Методи:
- has_time_limit(self) — повертає True якщо time_limit > 0.
- is_unlimited_attempts(self) — True якщо count_attempts == 0.
- has_pass_score_requirement(self) — True якщо pass_score > 0.
- has_attempts_left(self, user_attempts) — перевіряє, чи залишилися спроби (user_attempts < count_attempts або необмежено).
- is_passed(self, user_score) — перевіряє проходження: якщо pass_score == 0 повертає user_score >= 0, інакше user_score >= pass_score.
- clean(self) — валідація правил зв'язку: публічний тест не може бути прив'язаний до course/module; непублічний має бути прив'язаний до course або module; не можна прив'язати і до course і до module; якщо обидва вказані перевіряє сумісність module.course == course.
- save(self, *args, **kwargs) — викликає clean() перед збереженням.
- __str__ — повертає рядок з контекстом (for course/module або Public).

Meta:
- ordering = ['order', 'id'].
- constraints:
  - CheckConstraint на коректність зв'язування is_public/course/module.
  - UniqueConstraint fields=['course','title'] conditional if course not null.
  - UniqueConstraint fields=['module','title'] conditional if module not null.
  - UniqueConstraint fields=['course','order'] conditional.
  - UniqueConstraint fields=['module','order'] conditional.
  - CheckConstraint order > 0.
- indexes: conditional по course/module (title, order), та index по is_public.
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Index, Q
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser
from .base import BaseModel
from .course import Course
from .module import Module
from ..choices import CATEGORY_CHOICES, LEVELS


class Test(BaseModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_tests',
        blank=True,
        null=True,
        verbose_name=_("Course")
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='module_tests',
        blank=True,
        null=True,
        verbose_name=_("Module")
    )
    title = models.CharField(max_length=100, verbose_name=_("Test title"))
    description = models.TextField(max_length=500, blank=True, null=True, verbose_name=_("Test description"))
    time_limit = models.PositiveIntegerField(default=0, verbose_name=_("Time limit (in minutes)"))
    count_attempts = models.PositiveIntegerField(default=0, verbose_name=_("Count attempts"))
    pass_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name=_("Pass score")
    )
    randomize_questions = models.BooleanField(default=False, verbose_name=_("Randomize questions"))
    show_correct_answers = models.BooleanField(default=True, verbose_name=_("Show correct answers"))
    test_data_ids = models.JSONField(default=list, verbose_name=_("Mongo question IDs"))
    order = models.PositiveIntegerField(verbose_name=_("Test order"))
    is_public = models.BooleanField(default=False, db_index=True, verbose_name=_("Is public"))
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="tests",
        blank=True,
        null=True,
        verbose_name=_("Test owner (public tests only)"),
    )
    category = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Category"),
        choices=CATEGORY_CHOICES
    )
    level = models.CharField(
        max_length=100,
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_("Test level"),
        choices=LEVELS
    )

    def has_time_limit(self):
        """Перевіряє чи тест має обмеження за часом"""
        return self.time_limit > 0

    def is_unlimited_attempts(self):
        """Перевіряє чи тест має необмежену кількість спроб"""
        return self.count_attempts == 0

    def has_pass_score_requirement(self):
        """Перевіряє чи тест має мінімальний поріг проходження"""
        return self.pass_score > 0

    def has_attempts_left(self, user_attempts):
        """Перевіряє чи залишились спроби у користувача"""
        if self.is_unlimited_attempts():
            return True
        return user_attempts < self.count_attempts

    def is_passed(self, user_score: float) -> bool:
        """Перевіряє, чи користувач пройшов тест.
        Якщо викладач не встановив мінімальної кількості балів (pass_score == 0), то
        тест вважається пройденим при будь-якому результаті ≥ 0.
        """
        if not self.has_pass_score_requirement():
            return user_score >= 0
        return user_score >= self.pass_score

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.is_public:
            if self.course or self.module:
                raise ValidationError(_("Public test cannot be linked to course or module"))
            if not self.owner:
                raise ValidationError(_("Public test must have an owner"))
            return

        if not (self.course or self.module):
            raise ValidationError(_("Non-public test must be linked to either course or module"))
        if self.course and self.module:
            raise ValidationError(_("Test cannot be linked to both course and module"))
        if self.module and self.course and self.module.course_id != self.course_id:
            raise ValidationError(_("Module must belong to the specified course"))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.course_id:
            suffix = f" for {self.course.title}"
        elif self.module_id:
            suffix = f" for {self.module.title}"
        else:
            suffix = f" ({_('Public')})"
            if self.owner:
                suffix += f" by {self.owner.name} {self.owner.surname}"
        return f"{_('Test')} - {self.title}{suffix}"

    class Meta:
        db_table = "tests"
        verbose_name = _("Test")
        verbose_name_plural = _("Tests")
        ordering = ['order', 'id']
        constraints = [
            models.CheckConstraint(
                name="test_linkage_valid",
                check=(
                        Q(is_public=True, course__isnull=True, module__isnull=True) |
                        Q(is_public=False, course__isnull=False, module__isnull=True) |
                        Q(is_public=False, course__isnull=True, module__isnull=False)
                ),
            ),
            models.UniqueConstraint(
                fields=['course', 'title'],
                condition=Q(course__isnull=False),
                name='unique_test_title_per_course'
            ),
            models.UniqueConstraint(
                fields=['module', 'title'],
                condition=Q(module__isnull=False),
                name='unique_test_title_per_module'
            ),
            models.UniqueConstraint(
                fields=['course', 'order'],
                condition=Q(course__isnull=False),
                name='unique_test_order_per_course'
            ),
            models.UniqueConstraint(
                fields=['module', 'order'],
                condition=Q(module__isnull=False),
                name='unique_test_order_per_module'
            ),
            models.CheckConstraint(name="test_order_positive", check=Q(order__gt=0)),
        ]
        indexes = [
            Index(fields=['course', 'title'], name="ix_test_course_title", condition=Q(course__isnull=False)),
            Index(fields=['module', 'title'], name="ix_test_module_title", condition=Q(module__isnull=False)),
            Index(fields=['course', 'order'], name="ix_test_course_order", condition=Q(course__isnull=False)),
            Index(fields=['module', 'order'], name="ix_test_module_order", condition=Q(module__isnull=False)),
            Index(fields=['is_public'], name="ix_test_is_public"),
        ]
