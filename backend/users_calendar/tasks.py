from gettext import gettext as _

from celery import shared_task
from django.contrib.auth import get_user_model

from notifications.tasks import send_bulk_notification_email_task
from smartStudy_backend import settings
from users.models import CustomUser
from users_calendar.services import DailyCalendarSummaryService

User = get_user_model()


@shared_task(name='notifications.tasks.send_daily_reminders_task')
def send_daily_reminders_task():
    from notifications.models import Notification, NotificationsType
    from notifications.services.cache_service import NotificationsCache
    from asgiref.sync import async_to_sync

    users = CustomUser.objects.filter(
        is_active=True,
        settings__email_notifications=True
    ).select_related('settings')
    processed_user_ids = []

    for user in users:
        service = DailyCalendarSummaryService(user)
        personal_events, course_events = service.get_summary()

        if not personal_events and not course_events:
            continue

        message_parts = []

        if personal_events:
            message_parts.append(f"👤 {_('Personal events')}:")
            for p in personal_events:
                is_high = p.importance == 'high'
                importance_icon = "❗" if is_high else "🔹"
                message_parts.append(f"{importance_icon} {p.title}")

                Notification.objects.create(
                    user=user,
                    notification_type=NotificationsType.EVENT_REMINDER,
                    title=p.title,
                    message=p.description or _("Event reminder"),
                    event=p,
                    is_important=is_high
                )

        if course_events:
            if message_parts:
                message_parts.append("")

            message_parts.append(f"📚 {_('Curriculum')}:")
            for c in course_events:
                target = f"Lesson: {c.lesson.title}" if c.lesson else _("Testing")
                message_parts.append(f"📖 {c.course.title} — {target}")

                Notification.objects.create(
                    user=user,
                    notification_type=NotificationsType.MESSAGE_FROM_COURSE_OWNER,
                    title=f"{c.course.title}: {target}",
                    message=c.note or _("Time to learn!"),
                    course=c.course,
                    event=None,
                    is_important=False
                )

        if getattr(user.settings, 'email_notifications', True):
            send_bulk_notification_email_task.delay(
                recipient_list=[user.email],
                title= f"📅 {_('Your plan for today')}",
                message="\n".join(message_parts),
                personal_link=f"{settings.FRONTEND_URL}/calendar",
                link_text=_("Open the calendar")
            )

        processed_user_ids.append(user.id)

    if processed_user_ids:
        cache_service = NotificationsCache(user=users[0])
        async_to_sync(cache_service.invalidate_for_users_cache)(processed_user_ids)
