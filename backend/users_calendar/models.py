import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from courses.models import Course


class BaseUserCalendar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calendar",
        verbose_name=_("Calendar owner")
    )

    def __str__(self):
        return f"{_('Calendar')} - {self.user.email}"

    class Meta:
        db_table = "user_calendars"
        verbose_name = _("User calendar")
        verbose_name_plural = _("User calendars")


class EventImportance(models.TextChoices):
    LOW = 'low', _('Low')
    MEDIUM = 'medium', _('Medium')
    HIGH = 'high', _('High')


class CalendarEventBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_date = models.DateTimeField(_("Event date"), db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PersonalEvent(CalendarEventBase):
    calendar = models.ForeignKey(
        BaseUserCalendar,
        on_delete=models.CASCADE,
        related_name="personal_events",
        verbose_name=_("Calendar")
    )
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True, max_length=1000, default="")

    importance = models.CharField(
        _("Importance"),
        max_length=10,
        choices=EventImportance.choices,
        default=EventImportance.MEDIUM
    )

    link = models.URLField(_("Link"), null=True, blank=True)
    is_completed = models.BooleanField(_("Is completed"), default=False)
    completed_at = models.DateTimeField(_("Completed at"), null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.calendar.user.email})"

    class Meta:
        db_table = "personal_events"
        ordering = ['event_date']
        verbose_name = _("Personal event")
        verbose_name_plural = _("Personal events")
        indexes = [
            models.Index(fields=['calendar', 'event_date']),
            models.Index(fields=['is_completed']),
        ]


class CourseCalendarEvent(CalendarEventBase):
    calendar = models.ForeignKey(
        BaseUserCalendar,
        on_delete=models.CASCADE,
        related_name="course_events",
        verbose_name=_("Calendar")
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="calendar_events",
        verbose_name=_("Course")
    )
    note = models.CharField(_("Note"), max_length=255, blank=True)

    def __str__(self):
        return f"{self.course.title} - {self.calendar.user.email}"

    class Meta:
        db_table = "course_events"
        ordering = ['event_date']
        verbose_name = _("Course event")
        verbose_name_plural = _("Course events")
        indexes = [
            models.Index(fields=['calendar', 'event_date']),
        ]
