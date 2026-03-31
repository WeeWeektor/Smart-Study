from asgiref.sync import sync_to_async

from notifications.services.cache_service.base_cache import BaseCache
from notifications.services.course_owner_notification_service import CourseOwnerNotifications


class CourseOwnerNotificationCache(BaseCache):
    CACHE_TIMEOUT = 60 * 10

    def __init__(self, course_id, owner):
        self.course_id = course_id
        self.owner = owner
        self._key = f'notifications:course_owner_sent_message:owner_{owner.id}:course_{course_id}'

        super().__init__(key=self._key)

    async def get_course_owner_notification_cache(self):
        data = await sync_to_async(self.cache.get)(self.key, version=self.CACHE_VERSION, default=None)
        if data is not None:
            return data

        course_owner_notifications = CourseOwnerNotifications(self.owner, self.course_id)
        data = await course_owner_notifications.get_notifications()

        if data is not None:
            await sync_to_async(self.cache.set)(self.key, data, self.CACHE_TIMEOUT, self.CACHE_VERSION)
            await self.register_key()

        return data

    async def invalidate_course_owner_notification_cache(self):
        await sync_to_async(self.cache.delete)(self.key, version=self.CACHE_VERSION)
        self.logger.info(f"Cache invalidated for owner {self.owner.id} and course {self.course_id}")


