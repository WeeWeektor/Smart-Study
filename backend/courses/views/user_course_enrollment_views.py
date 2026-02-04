import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response, validate_uuid
from courses.models import Course, UserCourseEnrollment, Test, TestAttempt
from courses.serializers import CourseTestSummarySerializer
from courses.services.course_by_user import get_course_with_details_enrollment, create_course_enrollment, \
    update_enrollment_progress_sync


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

            from courses.services.cache_service import invalidate_courses_by_user_id_cache, \
                invalidate_course_enrollment_status_cache
            await invalidate_courses_by_user_id_cache(user_id)

            if finished_course:
                await invalidate_course_enrollment_status_cache(course_id)

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

        from courses.services.cache_service import get_course_enrollment_status_cache
        data = await get_course_enrollment_status_cache(course_id, user_id)

        if isinstance(data, dict):
            return success_response(data=data, message=gettext("Enrollment status retrieved successfully"), status=200)

        return error_response(data.get("message", gettext("Error retrieving enrollment status")),
                              status=data.get("status", 500))


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseTestResultsView(LocalizedView):
    """
        Повертає зведену статистику по всіх тестах курсу для конкретного студента.
        Використовується для сторінки CourseCompletion.
    """

    # TODO Винести логіку в сервіси + перевірити на коректність

    @login_required_async
    async def get(self, request, course_id):
        user = request.user

        course_id = validate_uuid(course_id)

        try:
            enrollment = await UserCourseEnrollment.objects.aget(user=user, course_id=course_id)

            results_data = await sync_to_async(self._get_test_results_data)(enrollment, course_id)

            serializer = CourseTestSummarySerializer(results_data, many=True)

            return success_response({"results": serializer.data})

        except UserCourseEnrollment.DoesNotExist:
            return error_response(gettext("Enrollment not found"), status=404)
        except Exception as e:
            return error_response(gettext(f"Error fetching test results: {str(e)}"), status=500)

    @staticmethod
    def _get_test_results_data(enrollment, course_id):
        tests = Test.objects.filter(
            Q(course_id=course_id) | Q(module__course_id=course_id)
        ).values(
            'id', 'title', 'module_id', 'pass_score', 'count_attempts'
        ).order_by('module__order', 'order')

        if not tests:
            return []

        test_ids = [t['id'] for t in tests]

        attempts = TestAttempt.objects.filter(
            enrollment=enrollment,
            test__id__in=test_ids
        ).values('test_id', 'score', 'passed')

        attempts_by_test = {}
        for attempt in attempts:
            t_id = attempt['test_id']
            if t_id not in attempts_by_test:
                attempts_by_test[t_id] = []
            attempts_by_test[t_id].append(attempt)

        final_results = []
        for test in tests:
            test_attempts = attempts_by_test.get(test['id'], [])

            attempts_used = len(test_attempts)

            is_passed = any(a['passed'] for a in test_attempts)

            best_score = max([a['score'] for a in test_attempts]) if test_attempts else 0.0

            final_results.append({
                'id': test['id'],
                'title': test['title'],
                'module_id': test['module_id'],
                'score': best_score,
                'pass_score': test['pass_score'],
                'passed': is_passed,
                'attempts_used': attempts_used,
                'max_attempts': test['count_attempts']
            })

        return final_results
