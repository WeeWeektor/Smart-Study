from asgiref.sync import sync_to_async
from django.db.models import Count

from notifications.models import Notification, NotificationsType


class CourseOwnerNotifications:
    def __init__(self, owner, course_id):
        self.owner = owner
        self.course_id = course_id

    def __fetch_notifications(self):
        queryset = (
            Notification.objects.filter(
                course_id=self.course_id,
                notification_type=NotificationsType.MESSAGE_FROM_COURSE_OWNER
            )
            .values('title', 'message', 'sent_at', 'personal_link', 'link_text')
            .annotate(recipients_count=Count('id'))
            .order_by('-sent_at')
        )
        return list(queryset)

    def __fetch_and_serialize(self):
        raw_data = self.__fetch_notifications()

        return [{
            "title": item['title'],
            "message": item['message'],
            "sent_at": item['sent_at'].strftime("%Y-%m-%dT%H:%M:%S"),
            "personal_link": item['personal_link'],
            "link_text": item['link_text'],
            "recipients_count": item['recipients_count'],
            "notification_type": "message_from_course_owner",
            "action_text": item['link_text'] or "Переглянути"
        } for item in raw_data]

    async def get_notifications(self):
        return await sync_to_async(self.__fetch_and_serialize)()

    async def __get_enrolled_students_ids(self):
        from courses.models import UserCourseEnrollment
        return [
            uid async for uid in
            UserCourseEnrollment.objects.filter(course_id=self.course_id).values_list('user_id', flat=True)
        ]

    def __execute_bulk_create(self, student_ids, title, message, personal_link, link_text):
        notifications = [
            Notification(
                user_id=sid,
                course_id=self.course_id,
                notification_type=NotificationsType.MESSAGE_FROM_COURSE_OWNER,
                title=title,
                message=message,
                personal_link=personal_link,
                link_text=link_text,
                is_important=True
            ) for sid in student_ids
        ]
        Notification.objects.bulk_create(notifications)
        return len(notifications)

    async def post_notification(self, title, message, personal_link=None, link_text=None):
        student_ids = await self.__get_enrolled_students_ids()

        if not student_ids:
            return 0

        count = await sync_to_async(self.__execute_bulk_create)(
            student_ids, title, message, personal_link, link_text
        )

        from notifications.services.cache_service import CourseOwnerNotificationCache
        cache_service = CourseOwnerNotificationCache(course_id=self.course_id, owner=self.owner)
        await cache_service.invalidate_course_owner_notification_cache()

        updated_data = await cache_service.get_course_owner_notification_cache()

        # TODO signals або інвалідація кешу для користувачів тут


        return count, updated_data
