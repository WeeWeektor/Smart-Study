from asgiref.sync import sync_to_async
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.models import Course
from courses.utils import generate_course_json_with_details_and_owner
from ml_model.recommender import courses_recommender


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseRecommendationsView(LocalizedView):
    @login_required_async
    async def get(self, request, course_id):
        status_param = request.GET.get('status', 'passed')
        limit_param = request.GET.get('limit', 6)

        if status_param not in ['passed', 'failed']:
            return error_response(_("Invalid status parameter. Must be 'passed' or 'failed'."), status=400)

        if not isinstance(int(limit_param), int) or int(limit_param) <= 0 or int(limit_param) > 100:
            return error_response(
                _("Invalid limit parameter. Must be an integer or in the interval from 1 to 100"),
                status=400
            )

        try:
            recommended_ids = await sync_to_async(courses_recommender.get_recommendations)(
                course_id=course_id,
                status=status_param,
                limit=int(limit_param)
            )

            from django.db.models import Case, When
            courses = []
            if recommended_ids:
                preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(recommended_ids)])
                courses_qs = Course.objects.filter(id__in=recommended_ids).order_by(preserved_order)
                courses = [course async for course in courses_qs]

            courses_data = await generate_course_json_with_details_and_owner(courses)

            return success_response({
                "courses_data": courses_data
            })

        except Exception as e:
            return error_response(_(f"Failed to generate recommendations {str(e)}"), status=500)
