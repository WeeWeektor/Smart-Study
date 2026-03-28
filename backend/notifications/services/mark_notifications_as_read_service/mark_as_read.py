from asgiref.sync import sync_to_async

from notifications.models import Notification
from notifications.services.cache_service import NotificationsCache


class MarkAsRead:
    def __init__(self, user, mark_all=False, notification_ids=None):
        self.user = user
        self.mark_all = mark_all
        self.notification_ids = notification_ids or []

    def __perform_to_update(self):
        if self.mark_all:
            return Notification.objects.filter(user=self.user, is_read=False).update(is_read=True)

        if self.notification_ids:
            return (Notification.objects
                    .filter(user=self.user, id__in=self.notification_ids, is_read=False)
                    .update(is_read=True))

        return 0

    async def mark_as_read(self):
        update_count = await sync_to_async(self.__perform_to_update)()

        cache_service = NotificationsCache(self.user)

        if update_count > 0:
            await cache_service.invalidate_notifications_cache()

        return await cache_service.get_notifications_cache()
