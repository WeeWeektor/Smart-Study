from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import success_response, error_response
from courses.models import Course
from courses.services.structure_course_module_action_service import get_course_structures


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseStructureView(LocalizedView):
    """View для отримання структури курсу"""

    @login_required_async
    async def get(self, request, course_id):
        try:
            course_structure_data = await get_course_structures(course_id)
            return success_response(course_structure_data)
        except ValidationError as e:
            return error_response(str(e), status=400)
        except Course.DoesNotExist:
            return error_response(_("Course not found."), status=404)
        except Exception as e:
            return error_response(f"{_("Error resaving course:")} {str(e)}", status=500)
