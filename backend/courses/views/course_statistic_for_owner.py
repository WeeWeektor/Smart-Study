from asgiref.sync import sync_to_async
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.utils import error_response, success_response
from courses.decorators import owner_course_required
from courses.models import Course
from courses.serializers import CourseStatisticForOwnerSerializer
from courses.services.course_actions_service import get_course_statistics_data


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseStatisticsView(LocalizedView):
    @owner_course_required
    async def get(self, request, course_id):
        try:
            @sync_to_async
            def get_data():
                _course = get_course_statistics_data(course_id)
                return CourseStatisticForOwnerSerializer(_course).data

            data = await get_data()
            return success_response(data=data)

        except Course.DoesNotExist:
            return error_response(gettext("Course not found."), status=404)
        except Exception as e:
            return error_response(f"{gettext("An error occurred while fetching course statistics:")} {str(e)}",
                                  status=500)
