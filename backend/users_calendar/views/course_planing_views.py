import json

from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import sanitize_input
from users_calendar.services.course_event_service import CreateCourseEvent, DeleteCourseEvents

# TODO переглянути всі gettext

@method_decorator(ensure_csrf_cookie, name="dispatch")
class CoursePlaningListCreateView(LocalizedView):
    @login_required_async
    async def get(self, request):
        from users_calendar.services.cache_service import CourseEventsCache
        cache_service = CourseEventsCache(request.user)
        try:
            data = await cache_service.get_course_events_cache()
            return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @login_required_async
    async def post(self, request):
        try:
            body_data = json.loads(request.body)

            if isinstance(body_data, list):
                data = [
                    {k: sanitize_input(v) if isinstance(v, str) else v for k, v in item.items()}
                    for item in body_data
                ]
            else:
                data = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in body_data.items()}

            create_course_events = CreateCourseEvent(request.user, data)
            count, events_list = await create_course_events.create_event()

            return JsonResponse({
                "created_count": count,
                "events": events_list
            }, status=status.HTTP_201_CREATED)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except DRFValidationError as e:
            return JsonResponse(e.detail, status=status.HTTP_400_BAD_REQUEST, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CoursePlaningDetailView(LocalizedView):
    @login_required_async
    async def delete(self, request, pk):
        try:
            service = DeleteCourseEvents(user=request.user, event_id=pk)
            success = await service.delete_events()

            if success:
                return HttpResponse(status=status.HTTP_204_NO_CONTENT)

            return JsonResponse({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# TODO якщо змінилось в календарі щось тоді оновлювати сповіщення також
# TODO баг: якщо пройти пару уроків\тестів і потім створити запис в календар цих уроків вони ніколи пройденими не стануть тільки якщо створити запис в календарі до проходження уроку\тесту тоді вони будуть відмічені як пройдені
