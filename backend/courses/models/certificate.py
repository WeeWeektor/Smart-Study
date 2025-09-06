"""Certificate
Клас: сертифікат, виданий користувачу за проходження курсу.

Поля:
- user: ForeignKey('users.CustomUser') — власник сертифікату, related_name='certificates'.
- course: ForeignKey('Course') — курс, related_name='certificates'.
- issued_at: DateTimeField(auto_now_add=True) — дата видачі.
- certificate_id: CharField(max_length=100, unique=True) — унікальний ідентифікатор сертифікату.
- is_valid: BooleanField(default=True) — чи дійсний сертифікат.

Методи:
- save(self, *args, **kwargs) — при відсутності certificate_id генерує його у форматі "CERT-{12 hex}", потім викликає super().save.

Meta:
- verbose_name/verbose_name_plural — локалізовані назви.
- constraints: UniqueConstraint(fields=['user','course'], name='unique_user_course_certificate').
- indexes: індекси по user та certificate_id.

Строкове представлення:
- повертає "Certificate {certificate_id} - {user.email}".
"""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel


class Certificate(BaseModel):
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name=_("User")
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name=_("Course")
    )
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Issued at"))
    certificate_id = models.CharField(max_length=100, unique=True, verbose_name=_("Certificate ID"))
    is_valid = models.BooleanField(default=True, verbose_name=_("Is valid"))

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course'],
                name='unique_user_course_certificate'
            ),
        ]
        indexes = [
            models.Index(fields=['user'], name="ix_certificate_user"),
            models.Index(fields=['certificate_id'], name="ix_certificate_id"),
        ]

    def __str__(self):
        return f"{_("Certificate")} {self.certificate_id} - {self.user.email}"
