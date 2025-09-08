import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response, sanitize_input, validate_uuid
from courses.decorators import teacher_required, owner_course_required
from courses.models import Course
from courses.services import get_cached_course_by_id, get_cached_all_courses, create_course, remove_course


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseView(LocalizedView):
    """View для роботи з курсами"""

    @login_required_async
    async def get(self, request, course_id=None):
        """Отримання всіх курсів або одного курсу за id"""
        if course_id:
            try:
                uuid_obj = validate_uuid(course_id)
                course = await sync_to_async(Course.objects.select_related('details', 'owner').get)(pk=uuid_obj)
                course_data = await get_cached_course_by_id(course)
                return success_response(course_data)
            except ValidationError as e:
                return error_response(str(e), status=400)
            except Course.DoesNotExist:
                return error_response(gettext("Course not found"), status=404)
            except Exception as e:
                return error_response(f"{gettext('Error retrieving course:')} {str(e)}", status=500)
        else:
            try:
                categories = request.GET.get('cate')
                if categories:
                    categories = [c.strip() for c in categories.split(",")]
                courses_data = await get_cached_all_courses(categories)
                return success_response({"courses": courses_data})
            except Exception as e:
                return error_response(f"{gettext('Error retrieving courses:')} {str(e)}", status=500)

    @login_required_async
    @teacher_required
    async def post(self, request):
        """Створення курсу викладачем"""

        data = json.loads(request.POST.get('data', '{}'))
        cover_file = request.FILES.get('cover_image')

        data = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in data.items()}

        try:
            course = await create_course(request.user, data, cover_file)

            return success_response({
                "message": gettext("Course created successfully"),
                "course_id": course.id,
                "cover_image": course.cover_image if course.cover_image else None
            })
        except ValidationError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response(f"{gettext("Error creating course:")} {str(e)}", status=500)

    @login_required_async
    @owner_course_required
    async def patch(self, request, course_id):
        """Редагування курсу за id власником курсу"""
        try:
            data = json.loads(request.body)
            data.get("is_published", False)

            return success_response({
                "message": gettext("Course edit successfully"),
                "course_id": course_id
            })
        except Exception as e:
            return error_response(f"{gettext('Error updating course:')} {str(e)}", status=500)

    @login_required_async
    @owner_course_required
    async def delete(self, request, course_id):
        """Видалення курсу за id власником курсу"""
        try:
            uuid_obj = validate_uuid(course_id)
            course = await sync_to_async(Course.objects.select_related('details').get)(pk=uuid_obj)
            return await remove_course(course)
        except ValidationError as e:
            return error_response(str(e), status=400)
        except Course.DoesNotExist:
            return error_response(gettext("Course not found"), status=404)
        except Exception as e:
            return error_response(f"{gettext('Error retrieving course:')} {str(e)}", status=500)
