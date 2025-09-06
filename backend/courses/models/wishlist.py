"""Wishlist
Клас: список бажань користувача (курс у вішлисті).

Поля:
- user: ForeignKey('users.CustomUser'), related_name='wishlist'.
- course: ForeignKey('Course'), related_name='wishlisted_by'.
- added_at: DateTimeField(auto_now_add=True).

Meta:
- constraints: UniqueConstraint(fields=['user','course']) — уникальність пари.
- indexes: Index(fields=['user','-added_at']).
- verbose_name/verbose_name_plural.

Строкове представлення:
- "{user.email} - {course.title}"
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel


class Wishlist(BaseModel):
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='wishlist',
        verbose_name=_("User")
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='wishlisted_by',
        verbose_name=_("Course")
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Added at"))

    class Meta:
        db_table = "user_wishlist"
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlists")
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course'],
                name='unique_user_course_wishlist'
            ),
        ]
        indexes = [
            models.Index(fields=['user', '-added_at'], name="ix_wishlist_user_added"),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
