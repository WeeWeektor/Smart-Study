from asgiref.sync import sync_to_async

from users_calendar.models import PersonalEvent
from users_calendar.serializers import PersonalEventSerializer


class GetPersonalEvents:
    def __init__(self, user):
        self.user = user

    def __fetch_and_serialize(self):
        events = PersonalEvent.objects.filter(calendar__user=self.user)
        serializer = PersonalEventSerializer(events, many=True)
        return serializer.data

    async def get_events(self):
        return await sync_to_async(self.__fetch_and_serialize, thread_sensitive=True)()
