from datetime import timedelta

from asgiref.sync import sync_to_async
from django.db.models import Q, F, Case, When, Value, CharField
from django.utils import timezone

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class UserNotifications:
    def __init__(self, user, archived=False):
        self.user = user
        self.archived = archived

    def __fetch_and_serialize(self):
        threshold = timezone.now() - timedelta(days=7)

        queryset = (
            Notification.objects
            .filter(user=self.user)
            .annotate(
                annotated_source_name=Case(
                    When(course__isnull=False, then=F('course__title')),
                    When(event__isnull=False, then=F('event__title')),
                    default=Value(None),
                    output_field=CharField(),
                )
            )
            .select_related('course', 'event')
            .order_by('-sent_at'))

        if self.archived:
            queryset = queryset.filter(is_read=True, sent_at__lt=threshold)
        else:
            queryset = queryset.filter(
                Q(is_read=False) | Q(is_read=True, sent_at__gte=threshold)
            )

        queryset = queryset[:100]

        return NotificationSerializer(queryset, many=True).data

    async def get_notifications(self):
        return await sync_to_async(self.__fetch_and_serialize)()
