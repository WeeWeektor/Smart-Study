import logging

from asgiref.sync import sync_to_async
from django.db import transaction
from rest_framework.exceptions import ValidationError as DRFValidationError

from users_calendar.models import BaseUserCalendar, CourseCalendarEvent
from users_calendar.serializers import CourseCalendarEventSerializer


class CreateCourseEvent:
    def __init__(self, user, data):
        self.user = user
        self.data = data

        from users_calendar.services.cache_service import CourseEventsCache
        self.cache_service = CourseEventsCache(user)

    @staticmethod
    def _perform_bulk_create(items, current_user):
        calendar, _ = BaseUserCalendar.objects.get_or_create(user=current_user)

        events_to_create = []
        for item in items:
            events_to_create.append(
                CourseCalendarEvent(
                    calendar=calendar,
                    course=item.get('course'),
                    module=item.get('module'),
                    lesson=item.get('lesson'),
                    module_test=item.get('module_test'),
                    course_test=item.get('course_test'),
                    event_date=item.get('event_date'),
                    note=item.get('note', ''),
                    link=item.get('link', '')
                )
            )

        with transaction.atomic():
            course_ids = list(set([i.get('course') for i in items]))
            CourseCalendarEvent.objects.filter(calendar=calendar, course_id__in=course_ids).delete()

            created_list = CourseCalendarEvent.objects.bulk_create(events_to_create)
            return len(created_list)

    async def create_event(self):
        try:
            bulk_serializer = CourseCalendarEventSerializer(data=self.data, many=True)
            is_valid = await sync_to_async(bulk_serializer.is_valid)(raise_exception=False)
            if not is_valid:
                logging.error(f"Validation failed: {bulk_serializer.errors}")
                raise DRFValidationError(bulk_serializer.errors)

            validated_items = bulk_serializer.validated_data

            created_count = await sync_to_async(self._perform_bulk_create)(validated_items, self.user)

            await self.cache_service.invalidate_course_events_cache()
            updated_list = await self.cache_service.get_course_events_cache()

            return created_count, updated_list

        except DRFValidationError as e:
            logging.exception('Error in create course event validation: ' + str(e))
            raise e
        except Exception as e:
            logging.exception(f"Unexpected error creating event for user {self.user.id}")
            raise e
