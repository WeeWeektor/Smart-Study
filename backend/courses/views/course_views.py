import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response, sanitize_input, validate_uuid, paginate_list
from courses.decorators import teacher_required, owner_course_required
from courses.models import Course
from courses.services import get_cached_instance_by_id, get_instance_cached_all, create_course, remove_course, \
    get_instance_cached_by_author_id
from courses.utils import categories_level_present
from django.http import JsonResponse


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseView(LocalizedView):
    """View для роботи з курсами"""

    @login_required_async
    async def get(self, request, course_id=None):
        """Отримання всіх курсів або одного курсу за id"""
        if course_id:
            course_data = await get_cached_instance_by_id("course", "courses_get", course_id)
            return success_response(course_data)
        else:
            author_id = request.GET.get("author")
            page = request.GET.get("page", 1)

            if not author_id:
                category_list, level = categories_level_present(request)
                courses_data = await get_instance_cached_all("courses", "courses_get", category_list, level)
            else:
                courses_data = await get_instance_cached_by_author_id("courses", "courses_get", author_id)

            if isinstance(courses_data, JsonResponse):
                return courses_data

            paged_data_dict = await sync_to_async(lambda: paginate_list(courses_data, int(page), 24))()

            return success_response({
                "page": int(page),
                "total_courses": len(courses_data),
                "total_pages": paged_data_dict["total_pages"],
                "courses": paged_data_dict["results"]
            })

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
            uuid_obj = validate_uuid(course_id)
            course = await sync_to_async(Course.objects.select_related('details').get)(pk=uuid_obj)
            # return await update_course(request, course) # TODO
        except Exception as e:  # TODO add specific exceptions
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
