import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.models import Course
from courses.services.cache_service import get_cached_instance_by_id
from courses.services.course_by_user import get_course_with_details_enrollment, create_course_enrollment, \
    update_enrollment_progress_sync


@method_decorator(ensure_csrf_cookie, name="dispatch")
class UserCourseEnrollmentView(LocalizedView):
    @login_required_async
    async def get(self, request, course_id):
        user_id = request.user.id

        course_data = await get_cached_instance_by_id("course", "courses_get", course_id)
        if isinstance(course_data, JsonResponse):
            return course_data

        course_data_with_enrollment = await get_course_with_details_enrollment(course_id, user_id, course_data)

        return course_data_with_enrollment

    @login_required_async
    async def post(self, request, course_id):
        user_id = request.user.id
        try:
            enrollment, created = await create_course_enrollment(course_id, user_id)

            status_code = 201 if created else 200
            message = "Enrollment created successfully." if created else "User already enrolled."

            return success_response({
                "message": message,
                "enrollment_id": str(enrollment.id),
                "course_id": str(course_id),
                "progress": float(enrollment.progress),
                "is_new": created
            }, status=status_code)

        except Course.DoesNotExist:
            return error_response(gettext("Course not found."), status=404)
        except ValidationError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response(f"Error start course enrollment: {str(e)}", status=500)

    @login_required_async
    async def patch(self, request, course_id):
        user_id = request.user.id
        try:
            body = json.loads(request.body)

            element_id = body.get('element_id')
            element_type = body.get('element_type')
            finished_course = body.get('finished_course', False)
            time_spent = body.get('time_spent')
            is_completed = body.get('is_completed', False)

            result = await sync_to_async(update_enrollment_progress_sync)(
                user_id=user_id,
                course_id=course_id,
                element_id=element_id,
                element_type=element_type,
                time_spent_seconds=time_spent,
                is_completed=is_completed,
                finished_course=finished_course
            )

            return success_response({
                "message": "Progress updated successfully",
                "data": result
            })

        except json.JSONDecodeError:
            return error_response("Invalid JSON", status=400)
        except Exception as e:
            return error_response(f"Error updating progress: {str(e)}", status=500)
