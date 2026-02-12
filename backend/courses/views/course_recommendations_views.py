from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.services.cache_service import get_course_recommendations_cache


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseRecommendationsView(LocalizedView):
    @login_required_async
    async def get(self, request, course_id):
        status_param = request.GET.get('status', 'passed')
        limit_param = request.GET.get('limit', 6)

        if status_param not in ['passed', 'failed']:
            return error_response(_("Invalid status parameter. Must be 'passed' or 'failed'."), status=400)

        try:
            limit = int(limit_param)
            if limit <= 0 or limit > 100:
                raise ValueError
        except (ValueError, TypeError):
            return error_response(
                _("Invalid limit parameter. Must be an integer or in the interval from 1 to 100"),
                status=400
            )

        try:
            courses_data = await get_course_recommendations_cache(course_id, status_param, limit)

            return success_response({
                "courses_data": courses_data
            })

        except Exception as e:
            return error_response(_(f"Failed to generate recommendations {str(e)}"), status=500)
