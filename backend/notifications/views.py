from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status

from common import LocalizedAPIView
from common.decorators import login_required_async
from courses.decorators import owner_course_required


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


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseAnnouncementView(LocalizedAPIView):
    @login_required_async
    async def get(self, request, course_id):
        '''тільки для викладача отримувати всі сповіщення для конкретного курсу'''
        pass

    @owner_course_required
    async def post(self, request, course_id):
        pass


@method_decorator(ensure_csrf_cookie, name="dispatch")
class MarkNotificationsAsReadView(LocalizedAPIView):
    @login_required_async
    async def post(self, request):
        pass
    # TODO можливо обєднати з нижнім


@method_decorator(ensure_csrf_cookie, name="dispatch")
class MarkAllNotificationsAsReadView(LocalizedAPIView):
    @login_required_async
    async def post(self, request):
        pass
