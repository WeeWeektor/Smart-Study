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
            return success_response(data=lesson_data, message=gettext("Lesson retrieved successfully"))
