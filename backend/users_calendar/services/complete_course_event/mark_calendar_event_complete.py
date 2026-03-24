import logging

from asgiref.sync import sync_to_async
from django.db.models import Q

from users_calendar.models import CourseCalendarEvent

logger = logging.getLogger(__name__)


class MarkCalendarEventComplete:
    def __init__(self, user, **kwargs):
        self.user = user
        self.lesson_id = kwargs.get('lesson_id')
        self.module_id = kwargs.get('module_id')
        self.module_test_id = kwargs.get('module_test_id')
        self.course_test_id = kwargs.get('course_test_id')

    def _update_db_status(self):
        filters = Q(calendar__user=self.user) & Q(is_completed=False)

        if self.lesson_id:
            filters &= Q(lesson_id=self.lesson_id)
        elif self.module_test_id:
            filters &= Q(module_test_id=self.module_test_id)
            if self.module_id:
                filters &= Q(module_id=self.module_id)
        elif self.course_test_id:
            filters &= Q(course_test_id=self.course_test_id)
        else:
            return False

        updated_count = CourseCalendarEvent.objects.filter(filters).update(is_completed=True)
        return updated_count > 0

    async def execute(self):
        try:
            success = await sync_to_async(self._update_db_status, thread_sensitive=True)()

            if success:
                from users_calendar.services.cache_service import CourseEventsCache
                cache_service = CourseEventsCache(self.user)
                await cache_service.invalidate_course_events_cache()
                return True

            return False
        except Exception as e:
            logger.error(f"Failed to mark event as complete: {e}")
            return False
