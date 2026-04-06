import logging

from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError as DRFValidationError

from users_calendar.models import PersonalEvent
from users_calendar.serializers import PersonalEventSerializer
from users_calendar.services.cache_service import PersonalEventsCache


class UpdatePersonalEvents:
    def __init__(self, user, event_id, data):
        self.user = user
        self.event_id = event_id
        self.data = data
        self.cache_service = PersonalEventsCache(user)

    def __perform_update(self):
        event = get_object_or_404(PersonalEvent, id=self.event_id, calendar__user=self.user)

        if 'is_completed' in self.data:
            if self.data['is_completed'] is True:
                self.data['completed_at'] = timezone.now()
            else:
                self.data['completed_at'] = None

        serializer = PersonalEventSerializer(
            event,
            data=self.data,
            partial=True,
            context={'user': self.user}
        )

        if serializer.is_valid(raise_exception=True):
            updated_event = serializer.save()
            return updated_event
        return None

    async def update_event(self):
        try:
            await sync_to_async(self.__perform_update, thread_sensitive=True)()
            await self.cache_service.invalidate_personal_events_cache()
            updated_list = await self.cache_service.get_personal_events_cache()
            return updated_list
        except DRFValidationError as e:
            logging.exception('Error in update personal event validation: ' + str(e))
            raise e
        except Exception as e:
            logging.exception(f"Unexpected error updating event for user {self.user.id}")
            raise e
