import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.models import Course, UserCourseEnrollment
from courses.services.course_by_user import get_course_with_details_enrollment, create_course_enrollment, \
    update_enrollment_progress_sync, get_test_results_data_for_user


@method_decorator(ensure_csrf_cookie, name="dispatch")
class UserCourseEnrollmentView(LocalizedView):
    @login_required_async
    async def get(self, request, course_id):
        user_id = request.user.id

        try:
            data_container = await get_course_with_details_enrollment(course_id, user_id, {})
            user_status = data_container.get('user_status')

            if not user_status:
                return error_response(gettext("Enrollment not found"), status=404)

            response_data = {
                "course_id": str(course_id),
                "user_id": str(user_id),
                **user_status
            }

            return success_response(response_data)

        except Exception as e:
            return error_response(gettext(f"Error retrieving enrollment: {str(e)}"), status=500)

    @login_required_async
    async def post(self, request, course_id):
        user_id = request.user.id
        try:
            enrollment, created = await create_course_enrollment(course_id, user_id)

            status_code = 201 if created else 200
            message = gettext("Enrollment created successfully.") if created else gettext("User already enrolled.")

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
            return error_response(gettext(f"Error start course enrollment: {str(e)}"), status=500)

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

            if element_type == 'lesson' and is_completed:
                from users_calendar.services.complete_course_event import MarkCalendarEventComplete
                completion = MarkCalendarEventComplete(user=request.user, lesson_id=element_id)
                await completion.execute()

            from courses.services.cache_service import invalidate_courses_by_user_id_cache, \
                invalidate_course_enrollment_status_cache
            await invalidate_courses_by_user_id_cache(user_id)

            if finished_course:
                await invalidate_course_enrollment_status_cache(course_id, user_id)

            return success_response({
                "message": gettext("Progress updated successfully"),
                "data": result
            })

        except json.JSONDecodeError:
            return error_response(gettext("Invalid JSON"), status=400)
        except Exception as e:
            return error_response(gettext(f"Error updating progress: {str(e)}"), status=500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class UserCourseEnrollmentStatusView(LocalizedView):
    @login_required_async
    async def get(self, request, course_id):
        user_id = request.user.id

        try:
            from courses.services.cache_service import get_course_enrollment_status_cache
            data = await get_course_enrollment_status_cache(course_id, user_id)

            if data is None or "error" in data:
                return error_response(gettext("Error retrieving enrollment status"), status=500)

            if isinstance(data, dict):
                return success_response(
                    data=data,
                    message=gettext("Enrollment status retrieved successfully"),
                    status=200
                )

            return error_response(gettext("Unknown error"), status=500)

        except Exception as e:
            return error_response(gettext(f'Error retrieve course enrollment status: {str(e)}'), status=500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseTestResultsView(LocalizedView):
    """
        Повертає зведену статистику по всіх тестах курсу для конкретного студента.
        Використовується для сторінки CourseCompletion.
    """

    @login_required_async
    async def get(self, request, course_id):
        try:
            serializer_data = await get_test_results_data_for_user(course_id, request.user)

            return success_response({"results": serializer_data})

        except UserCourseEnrollment.DoesNotExist:
            return error_response(gettext("Enrollment not found"), status=404)
        except Exception as e:
            return error_response(gettext(f"Error fetching test results: {str(e)}"), status=500)
