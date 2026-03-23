import logging

from asgiref.sync import sync_to_async
from django.core.cache import caches

from common.services import register_cache_key
from users_calendar.services.course_event_service import GetCourseEvents

logger = logging.getLogger(__name__)

class CourseEventsCache:
    CACHE_TIMEOUT = 60 * 20
    CACHE_VERSION = 1
    CACHE_NAME = "calendar_events"

    def __init__(self, user):
        self.user = user
        self.key = f'course_events:user_{user.id}'
        self.cache = caches[self.CACHE_NAME]

    async def __register_cache_key(self):
        try:
            await register_cache_key(self.key, self.CACHE_NAME)
        except Exception as e:
            logger.error(f"Failed to register cache key {self.key}: {e}")

    async def get_course_events_cache(self):
        data = await sync_to_async(self.cache.get)(self.key, version=self.CACHE_VERSION, default=None)
        if data is not None:
            return data

        user_events = GetCourseEvents(self.user)
        data = await user_events.get_events()
        if data is not None:
            await sync_to_async(self.cache.set)(self.key, data, self.CACHE_TIMEOUT, self.CACHE_VERSION)
            await self.__register_cache_key()

        return data

    async def invalidate_course_events_cache(self):
        await sync_to_async(self.cache.delete)(self.key, version=self.CACHE_VERSION)
        logger.info(f"Cache invalidated for user {self.user.id}")
