from django.utils import timezone

from users_calendar.models import CourseCalendarEvent, PersonalEvent


class DailyCalendarSummaryService:
    def __init__(self, user):
        self.user = user
        now = timezone.now()
        self.today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    def get_summary(self):
        personal = PersonalEvent.objects.filter(
            calendar__user=self.user,
            event_date__range=(self.today_start, self.today_end),
            is_completed=False
        )

        courses = CourseCalendarEvent.objects.filter(
            calendar__user=self.user,
            event_date__range=(self.today_start, self.today_end),
            is_completed=False
        ).select_related('course', 'lesson', 'module_test', 'course_test')

        return list(personal), list(courses)
