import json

from asgiref.sync import sync_to_async
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.choices import VALID_CATEGORIES_CHOICES
from courses.decorators import teacher_required, owner_course_required
from courses.models import Course, CourseMeta
from courses.services import get_cached_course_by_id, get_cached_all_courses
from courses.utils import validate_choice


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseView(LocalizedView):
    """View для роботи з курсами"""

    @login_required_async
    async def get(self, request, course_id=None):
        """Отримання всіх курсів або одного курсу за id"""
        if course_id:
            try:
                course = await sync_to_async(Course.objects.select_related('details', 'owner').get)(pk=course_id)
                course_data = await get_cached_course_by_id(course)
                return success_response(course_data)
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
        try:
            data = json.loads(request.body)

            required_fields = ["title", "description", "category"]
            for field in required_fields:
                if field not in data:
                    return error_response(f"{gettext('Missing required field:')} {field}", status=400)

            validate_category = validate_choice(data.get("category"), VALID_CATEGORIES_CHOICES, gettext("category"))
            if validate_category:
                return validate_category

            @sync_to_async
            def create_course():
                course = Course.objects.create(
                    title=data["title"].strip(),
                    description=data["description"].strip(),
                    category=data["category"],
                    owner_id=request.user,
                    is_published=data.get("is_published", False)
                )
                CourseMeta.objects.create(course=course)
                return course

            course = await create_course()

            return success_response({
                "message": gettext("Course created successfully"),
                "course_id": course.id
            })
        except Exception as e:
            return error_response(f"{gettext("Error creating course:")} {str(e)}", status=500)

    @login_required_async
    @owner_course_required
    async def patch(self, request, course_id):
        """Редагування курсу за id власником курсу"""
        try:
            data = json.loads(request.body)

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
        pass
