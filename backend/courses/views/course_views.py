import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response, sanitize_input, validate_uuid, paginate_list
from courses.decorators import teacher_required, owner_course_required
from courses.models import Course
from courses.services import parse_multipart_request
from courses.services.cache_service import get_cached_instance_by_id, get_instance_cached_all, \
    get_instance_cached_by_author_id
from courses.services.course_actions_service import create_course, remove_course, update_course, \
    update_published_course_with_structure
from courses.utils import categories_level_sort_present, average_rating, certificates_issued, count_announcements, \
    course_structure


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseView(LocalizedView):
    """View для роботи з курсами"""

    @login_required_async
    async def get(self, request, course_id=None, search_query=None):
        """Отримання всіх курсів або одного курсу за id"""
        if course_id:
            course_data = await get_cached_instance_by_id("course", "courses_get", course_id)
            if isinstance(course_data, JsonResponse):
                return course_data
            return success_response(course_data)
        else:
            author_id = request.GET.get("author")
            page = request.GET.get("page", 1)
            status = request.GET.get("status")

            category_list, level, sort_keys = categories_level_sort_present(request)

            if not author_id:
                courses_data = await get_instance_cached_all("courses", "courses_get", category_list, level, sort_keys,
                                                             ) # TODO search_query
            else:
                courses_data = await get_instance_cached_by_author_id("courses", "courses_get", author_id, sort_keys,
                                                                      status) # TODO search_query

            if isinstance(courses_data, JsonResponse):
                return courses_data

            average_rat = average_rating(courses_data)
            certificates_issue = certificates_issued(courses_data)
            count_ann = count_announcements(courses_data)

            paged_data_dict = await sync_to_async(lambda: paginate_list(courses_data, int(page), 24))()

            return success_response({
                "page": int(page),
                "total_courses": len(courses_data),
                "total_pages": paged_data_dict["total_pages"],
                "courses": paged_data_dict["results"],
                "average_rating": average_rat,
                "certificates_issued": certificates_issue,
                "count_announcements": count_ann
            })

    @teacher_required
    async def post(self, request):
        """Створення курсу викладачем"""

        data = json.loads(request.POST.get('data', '{}'))
        cover_file = request.FILES.get('cover_image')
        # test_image_file = request.FILES.get('imageFile')

        data = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in data.items()}

        try:
            course = await create_course(request.user, data, cover_file)
            course_id = str(course.id)


            if 'courseStructure' in data:
                await course_structure(data['courseStructure'], request.user, course_id)

            return success_response({
                "message": gettext("Course created successfully"),
                "course_id": course_id,
                "cover_image": course.cover_image if course.cover_image else None
            })
        except ValidationError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response(f"{gettext("Error creating course:")} {str(e)}", status=500)

    @owner_course_required
    async def patch(self, request, course_id):
        """Редагування курсу за id власником курсу"""

        parsed_data, files, raw_form, parse_error = parse_multipart_request(request)
        if parse_error:
            return parse_error

        cover_file = files.get('cover_image') if files else None
        change_info_course = raw_form.get('change_info_course', 'false').lower()
        change_structure_course = raw_form.get('change_structure_course', 'false').lower()

        if not parsed_data and not cover_file:
            return error_response('No data provided for update', status=400)

        data = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in parsed_data.items()}

        try:
            uuid_obj = validate_uuid(course_id)
            course = await sync_to_async(Course.objects.select_related('details').get)(pk=uuid_obj)

            if course.is_published and change_structure_course == 'true':
                return await update_published_course_with_structure(course)
            elif change_info_course == 'true':
                return await update_course(course, data, cover_file)
        except ValidationError as e:
            return error_response(str(e), status=400)
        except Course.DoesNotExist:
            return error_response(gettext("Course not found"), status=404)
        except Exception as e:
            return error_response(f"{gettext('Error updating course:')} {str(e)}", status=500)

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
            return error_response(f"{gettext('Course deletion error:')} {str(e)}", status=500)
