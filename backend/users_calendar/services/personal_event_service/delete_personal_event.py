from users_calendar.models import PersonalEvent
from users_calendar.services.cache_service import PersonalEventsCache


class DeletePersonalEvents:
    def __init__(self, user, event_id):
        self.user = user
        self.event_id = event_id
        self.cache_service = PersonalEventsCache(user)

    async def delete_events(self):
        queryset = PersonalEvent.objects.filter(
            pk=self.event_id,
            calendar__user=self.user
        )

        count, _ = await queryset.adelete()

        if count > 0:
            await self.cache_service.invalidate_personal_events_cache()
            return True

        return False
