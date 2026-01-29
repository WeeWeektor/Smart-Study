from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.services.cache_service import courses_by_user_id_cache


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CoursesByUserView(LocalizedView):
    @login_required_async
    async def get(self, request):
        user_id = request.user.id
        if not user_id:
            return error_response(gettext("user id parameter is required."), status=400)

        try:
            courses = await courses_by_user_id_cache(user_id)
            return success_response({
                "in_wishlist": courses[0],
                "is_enrolled": courses[1],
                "is_completed": courses[2],
            })
        except Exception as e:
            return error_response(gettext("Error retrieving courses") + str(e), status=500)
