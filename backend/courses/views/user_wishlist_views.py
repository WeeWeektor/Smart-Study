from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.services.course_by_user import add_course_to_wishlist, remove_course_from_wishlist


@method_decorator(ensure_csrf_cookie, name="dispatch")
class UserWishlistView(LocalizedView):
    async def _handle_wishlist_action(self, request, course_id, service_function, success_message, error_message, result_key):
        user_id = request.user.id

        if not user_id or not course_id:
            return error_response(gettext("user id and course id parameters are required."), status=400)

        try:
            result = await service_function(user_id, course_id)
            return success_response({
                "message": success_message,
                result_key: result
            })

        except ValidationError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response(f"{error_message} {str(e)}", status=500)

    @login_required_async
    async def post(self, request, course_id):
        return await self._handle_wishlist_action(
            request,
            course_id,
            service_function=add_course_to_wishlist,
            success_message=gettext("Course added to wishlist successfully."),
            error_message=gettext("Error add course to wishlist of users:"),
            result_key="added_course"
        )

    @login_required_async
    async def delete(self, request, course_id):
        return await self._handle_wishlist_action(
            request,
            course_id,
            service_function=remove_course_from_wishlist,
            success_message=gettext("Course removed from wishlist successfully."),
            error_message=gettext("Error remove course from wishlist of users:"),
            result_key="removed_course"
        )

