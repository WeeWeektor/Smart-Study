import logging

from asgiref.sync import sync_to_async
from rest_framework.exceptions import ValidationError as DRFValidationError

from users_calendar.serializers import PersonalEventSerializer
from users_calendar.services.cache_service import PersonalEventsCache


class CreatePersonalEvent:
    def __init__(self, user, data):
        self.user = user
        self.data = data
        self.cache_service = PersonalEventsCache(user)

    def __perform_creation(self):
        if 'date' in self.data:
            self.data['event_date'] = self.data.pop('date')

        self.data['description'] = self.data.get('description') or ""
        self.data['link'] = self.data.get('link') or ""

        serializer = PersonalEventSerializer(
            data=self.data,
            context={'user': self.user}
        )

        serializer.is_valid(raise_exception=True)
        return serializer.save()

    async def create_event(self):
        try:
            await sync_to_async(self.__perform_creation, thread_sensitive=True)()
            await self.cache_service.invalidate_personal_events_cache()
            updated_list = await self.cache_service.get_personal_events_cache()
            return updated_list

        except DRFValidationError as e:
            logging.exception('Error in create personal event validation: ' + str(e))
            raise e
        except Exception as e:
            logging.exception(f"Unexpected error creating event for user {self.user.id}")
            raise e
