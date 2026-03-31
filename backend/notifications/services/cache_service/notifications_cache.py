from asgiref.sync import sync_to_async
from django.core.cache import caches

from notifications.services.cache_service.base_cache import BaseCache
from notifications.services.user_notification_service import UserNotifications


class NotificationsCache(BaseCache):
    CACHE_TIMEOUT = 60 * 20

    def __init__(self, user, **kwargs):
        self.user = user
        self.archived_notifications = kwargs.get('archived_notifications', False)

        current_key = self.get_user_cache_key(
            user.id) if not self.archived_notifications else self.get_user_archived_cache_key(user.id)

        super().__init__(key=current_key)
        self.cache = caches[self.CACHE_NAME]

    async def get_notifications_cache(self):
        data = await sync_to_async(self.cache.get)(self.key, version=self.CACHE_VERSION, default=None)
        if data is not None:
            return data

        user_notifications = UserNotifications(self.user, archived=self.archived_notifications)
        data = await user_notifications.get_notifications()

        if data is not None:
            await sync_to_async(self.cache.set)(self.key, data, self.CACHE_TIMEOUT, self.CACHE_VERSION)
            await self.register_key()

        return data

    async def invalidate_notifications_cache(self):
        keys = [self.get_user_cache_key(self.user.id), self.get_user_archived_cache_key(self.user.id)]
        await sync_to_async(self.cache.delete_many)(keys, version=self.CACHE_VERSION)
        self.logger.info(f"Cache invalidated for user {self.user.id}")
