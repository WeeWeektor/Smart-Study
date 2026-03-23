from asgiref.sync import sync_to_async

from users_calendar.models import CourseCalendarEvent
from users_calendar.serializers import CourseCalendarEventSerializer


class GetCourseEvents:
    def __init__(self, user):
        self.user = user

    def __fetch_and_serialize(self):
        events = CourseCalendarEvent.objects.filter(calendar__user=self.user)
        serializer = CourseCalendarEventSerializer(events, many=True)
        return serializer.data

    async def get_events(self):
        return await sync_to_async(self.__fetch_and_serialize, thread_sensitive=True)()
