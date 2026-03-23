from users_calendar.models import CourseCalendarEvent


class DeleteCourseEvents:
    def __init__(self, user, event_id):
        self.user = user
        self.event_id = event_id

        from users_calendar.services.cache_service import CourseEventsCache
        self.cache_service = CourseEventsCache(user)

    async def delete_events(self):
        queryset = CourseCalendarEvent.objects.filter(
            pk=self.event_id,
            calendar__user=self.user
        )

        count, _ = await queryset.adelete()

        if count > 0:
            await self.cache_service.invalidate_course_events_cache()
            return True

        return False
