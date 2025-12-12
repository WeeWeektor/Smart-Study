from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.translation import gettext

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.services.cache_service import get_cached_instance_by_id


class LessonView(LocalizedView):
    @login_required_async
    async def get(self, request, lesson_id=None):
        if lesson_id is None:
            return error_response(gettext("Invalid request"), status=400)
        else:
            lesson_data = await get_cached_instance_by_id("lesson", "courses_get", lesson_id)
            return success_response({"lesson_data": lesson_data})


    async def post(self, request):  #  TODO Можливо видалити цей метод і подібні йому якщо курси та структура курсів будуть створюватися тільки через курс сервіс
        print(request.POST.get("data"))
        return success_response("Post request received")
