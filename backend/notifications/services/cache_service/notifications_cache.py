import logging

from asgiref.sync import sync_to_async
from django.core.cache import caches

from common.services import register_cache_key
from notifications.services.user_notification_service import UserNotifications

logger = logging.getLogger(__name__)


class NotificationsCache:
    CACHE_TIMEOUT = 60 * 20
    CACHE_VERSION = 1
    CACHE_NAME = "calendar_events"
    _background_tasks = set()

    def __init__(self, user, **kwargs):
        self.user = user
        self.archived_notifications = kwargs.get('archived_notifications', False)

        self.active_key = f'notifications:current:user_{user.id}'
        self.archived_key = f'notifications:archived:user_{user.id}'

        self.cache = caches[self.CACHE_NAME]
        self.current_key = self.active_key if not self.archived_notifications else self.archived_key

    async def __register_cache_key(self):
        try:
            await register_cache_key(self.current_key, self.CACHE_NAME)
        except Exception as e:
            logger.error(f"Failed to register cache key {self.current_key}: {e}")

    async def get_notifications_cache(self):
        data = await sync_to_async(self.cache.get)(self.current_key, version=self.CACHE_VERSION, default=None)
        if data is not None:
            return data

        user_notifications = UserNotifications(self.user, archived=self.archived_notifications)
        data = await user_notifications.get_notifications()

        if data is not None:
            await sync_to_async(self.cache.set)(self.current_key, data, self.CACHE_TIMEOUT, self.CACHE_VERSION)
            await self.__register_cache_key()

        return data

    async def invalidate_notifications_cache(self):
        await sync_to_async(self.cache.delete_many)([self.active_key, self.archived_key], version=self.CACHE_VERSION)
        logger.info(f"Cache invalidated for user {self.user.id}")
