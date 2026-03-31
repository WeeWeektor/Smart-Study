import json

from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import sanitize_input
from users_calendar.services.personal_event_service import CreatePersonalEvent, UpdatePersonalEvents, \
    DeletePersonalEvents


@method_decorator(ensure_csrf_cookie, name="dispatch")
class PersonalEventListCreateView(LocalizedView):
    @login_required_async
    async def get(self, request):
        from users_calendar.services.cache_service import PersonalEventsCache
        cache_service = PersonalEventsCache(request.user)
        try:
            data = await cache_service.get_personal_events_cache()
            return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @login_required_async
    async def post(self, request):
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)
            data = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in data.items()}

            create_personal_events = CreatePersonalEvent(request.user, data)
            full_events_list = await create_personal_events.create_event()

            return JsonResponse(full_events_list, status=status.HTTP_201_CREATED, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except DRFValidationError as e:
            return JsonResponse(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class PersonalEventDetailView(LocalizedView):
    @login_required_async
    async def patch(self, request, pk):
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)
            data = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in data.items()}

            service = UpdatePersonalEvents(user=request.user, event_id=pk, data=data)
            full_events_list = await service.update_event()

            return JsonResponse(full_events_list, status=status.HTTP_200_OK, safe=False)

        except DRFValidationError as e:
            return JsonResponse(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @login_required_async
    async def delete(self, request, pk):
        try:
            service = DeletePersonalEvents(user=request.user, event_id=pk)
            success = await service.delete_events()

            if success:
                return HttpResponse(status=status.HTTP_204_NO_CONTENT)

            return JsonResponse({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
