"""TestAttempt
Клас: спроба користувача пройти тест.

Поля:
- user: ForeignKey('users.CustomUser'), related_name='test_attempts'.
- test: ForeignKey('Test'), related_name='attempts'.
- started_at: DateTimeField(auto_now_add=True).
- completed_at: DateTimeField(null=True, blank=True).
- score: FloatField(default=0.0).
- passed: BooleanField(default=False).
- answers_data: JSONField(default=dict) — відповіді/метадані.
- attempt_number: PositiveIntegerField — номер спроби.

Meta:
- ordering = ['-started_at'].
- indexes: Index(fields=['user','test']), Index(fields=['test','-started_at']).

Строкове представлення:
- "{test.title} - {user.email} (спроба {attempt_number})"
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel


class TestAttempt(BaseModel):
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='test_attempts',
        verbose_name=_("User"),
    )
    test = models.ForeignKey(
        'Test',
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name=_("Test"),
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Started at"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed at"))
    score = models.FloatField(default=0.0, verbose_name=_("Score"))
    passed = models.BooleanField(default=False, verbose_name=_("Passed"))
    answers_data = models.JSONField(default=dict, verbose_name=_("Answers Data"))
    attempt_number = models.PositiveIntegerField(verbose_name=_("Attempt Number"))

    class Meta:
        verbose_name = _("Test Attempt")
        verbose_name_plural = _("Test Attempts")
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'test'], name="ix_attempt_user_test"),
            models.Index(fields=['test', '-started_at'], name="ix_attempt_test_started"),
        ]

    def __str__(self):
        return f"{self.test.title} - {self.user.email} (спроба {self.attempt_number})"
