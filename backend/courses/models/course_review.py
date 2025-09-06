"""CourseReview
Клас: відгук користувача про курс.

Поля:
- course: ForeignKey('Course'), related_name='reviews'.
- user: ForeignKey('users.CustomUser'), related_name='course_reviews'.
- rating: PositiveIntegerField (validators 1..5).
- comment: TextField(max_length=1000).
- created_at: DateTimeField(auto_now_add=True).
- is_verified: BooleanField(default=False).

Meta:
- constraints: UniqueConstraint(fields=['user','course'], name='unique_user_course_review') — один відгук користувача на курс.
- indexes: Index(fields=['course','-created_at']), Index(fields=['rating']).
- verbose_name/verbose_name_plural.

Строкове представлення:
- "{course.title} - {user.email} ({rating}/5)"
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel


class CourseReview(BaseModel):
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_("Course"),
    )
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='course_reviews',
        verbose_name=_("User"),
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Rating (1-5)"),
    )
    comment = models.TextField(max_length=1000, verbose_name=_("Comment"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    is_verified = models.BooleanField(default=False, verbose_name=_("Is verified"))

    class Meta:
        db_table = "course_reviews"
        verbose_name = _("Course Review")
        verbose_name_plural = _("Course Reviews")
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course'],
                name='unique_user_course_review'
            ),
        ]
        indexes = [
            models.Index(fields=['course', '-created_at'], name="ix_review_course_created"),
            models.Index(fields=['rating'], name="ix_review_rating"),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.user.email} ({self.rating}/5)"
