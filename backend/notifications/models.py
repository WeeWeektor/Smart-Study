import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationsType(models.TextChoices):
    EVENT_REMINDER = 'event_reminder', _('Event reminder')
    MESSAGE_FROM_COURSE_OWNER = 'message_from_course_owner', _('Message from course owner')
    ACHIEVEMENT_UNLOCKED = 'achievement_unlocked', _('Achievement unlocked')
    DEFAULT = 'default', _('Default')


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_("User")
    )

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='announcements',
        verbose_name=_("Course")
    )
    event = models.ForeignKey(
        'users_calendar.PersonalEvent',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reminders',
        verbose_name=_("Personal event")
    )

    sent_at = models.DateTimeField(_("Sent at"), auto_now_add=True, db_index=True)
    notification_type = models.CharField(
        _("Notification type"),
        max_length=50,
        choices=NotificationsType.choices,
        default=NotificationsType.DEFAULT
    )
    is_important = models.BooleanField(_("Is important"), default=False)
    is_read = models.BooleanField(_("Is read"), default=False, db_index=True)

    title = models.CharField(_("Title"), max_length=255)
    message = models.TextField(_("Message"), blank=True, max_length=1000, default="")

    personal_link = models.URLField(_("External Link"), null=True, blank=True)
    link_text = models.CharField(
        _("Link Text"),
        max_length=50,
        blank=True,
        default="",
        help_text=_("Текст на кнопці для персонального посилання")
    )

    class Meta:
        db_table = "notifications"
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-sent_at']),
            models.Index(fields=['-sent_at']),
        ]

    def __str__(self):
        return f"{self.title} -> {self.user.email}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    def clean(self):
        if self.notification_type == NotificationsType.EVENT_REMINDER and not self.event:
            raise ValidationError(_("Для нагадування про подію необхідно вказати івент."))

        if self.notification_type == NotificationsType.MESSAGE_FROM_COURSE_OWNER and not self.course:
            raise ValidationError(_("Повідомлення від власника курсу повинно мати прив'язку до курсу."))

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.notification_type == NotificationsType.MESSAGE_FROM_COURSE_OWNER:
            self.is_important = True

        super().save(*args, **kwargs)

    @property
    def internal_url(self):
        """Посилання на внутрішній ресурс (курс/календар/профіль)"""
        if self.notification_type == NotificationsType.MESSAGE_FROM_COURSE_OWNER and self.course:
            return f"/course-review/{self.course.id}/"
        if self.notification_type == NotificationsType.EVENT_REMINDER:
            return "/calendar/"
        if self.notification_type == NotificationsType.ACHIEVEMENT_UNLOCKED:
            return "/profile/"
        return None

    @property
    def external_url(self):
        """Посилання на зовнішній ресурс (Zoom тощо)"""
        return self.personal_link

    @property
    def action_text(self):
        """Текст для кнопки на фронтенді"""
        if self.link_text:
            return self.link_text
        if self.personal_link:
            return _("Перейти за посиланням")
        if self.course:
            return _("До курсу")
        return _("Переглянути")
