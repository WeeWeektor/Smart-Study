import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status

from common import LocalizedAPIView
from common.decorators import login_required_async
from common.utils import validate_uuid, sanitize_input
from courses.decorators import owner_course_required
from notifications.services.course_owner_notification_service import CourseOwnerNotifications
from notifications.services.mark_notifications_as_read_service import MarkAsRead


@method_decorator(ensure_csrf_cookie, name="dispatch")
class NotificationView(LocalizedAPIView):
    @login_required_async
    async def get(self, request):
        params = getattr(request, 'query_params', request.GET)
        archived_param = params.get('archived', 'false').lower()
        archived = archived_param == 'true'

        from notifications.services.cache_service import NotificationsCache
        cache_service = NotificationsCache(request.user, archived_notifications=archived)

        try:
            data = await cache_service.get_notifications_cache()
            return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# TODO переглянути всі gettext

@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseAnnouncementView(LocalizedAPIView):
    @owner_course_required
    async def get(self, request, course_id):
        course_id = validate_uuid(course_id)

        from notifications.services.cache_service import CourseOwnerNotificationCache
        cache_service = CourseOwnerNotificationCache(
            course_id=course_id,
            owner=request.user
        )

        try:
            data = await cache_service.get_course_owner_notification_cache()

            if not data:
                return JsonResponse([], status=status.HTTP_200_OK, safe=False)

            return JsonResponse(data, status=status.HTTP_200_OK, safe=False)

        except Exception as e:
            return JsonResponse(
                {"error": f"Failed to fetch course announcements: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @owner_course_required
    async def post(self, request, course_id):
        course_id = validate_uuid(course_id)

        try:
            body_data = json.loads(request.body)
            title = sanitize_input(body_data.get('title'))
            message = sanitize_input(body_data.get('message'))
            personal_link = body_data.get('personal_link')
            link_text = sanitize_input(body_data.get('link_text', ''))

            if not title or not message:
                return JsonResponse(
                    {"error": "Title and message are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            service = CourseOwnerNotifications(owner=request.user, course_id=course_id)
            count, updated_history = await service.post_notification(
                title=title,
                message=message,
                personal_link=personal_link,
                link_text=link_text
            )

            if count == 0:
                return JsonResponse(
                    {"message": "No students to notify"},
                    status=status.HTTP_200_OK
                )

            return JsonResponse(updated_history, status=status.HTTP_201_CREATED, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse(
                {"error": f"Failed to post announcement: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(ensure_csrf_cookie, name="dispatch")
class MarkNotificationsAsReadView(LocalizedAPIView):
    @login_required_async
    async def post(self, request):
        try:
            body_data = json.loads(request.body)

            mark_all = body_data.get('mark_all', False)
            if isinstance(mark_all, str):
                mark_all = mark_all.lower() == 'true'

            notification_ids = body_data.get('notification_ids', [])
            if isinstance(notification_ids, list):
                notification_ids = [validate_uuid(str(id_)) for id_ in notification_ids]

            service = MarkAsRead(
                user=request.user,
                mark_all=mark_all,
                notification_ids=notification_ids,
            )

            refreshed_notifications = await service.mark_as_read()

            return JsonResponse(
                refreshed_notifications,
                status=status.HTTP_200_OK,
                safe=False
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
