import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import success_response, paginate_list, sanitize_input, error_response, validate_uuid
from courses.decorators import permission_test_required
from courses.models import Test, Course, Module
from courses.services import parse_multipart_request
from courses.services.cache_service import get_instance_cached_all, get_instance_cached_by_author_id, \
    get_cached_instance_by_id
from courses.services.test_actions_service import create_test, remove_test, validate_test_editable, update_test, \
    submit_test_attempt, history_and_config
from courses.utils import categories_level_sort_present

# TODO image_url додати логіку збереження оновлення і видалення зображення для questions (Через create_course_with_structure зберігається в монго лише назва файлу)

class BaseTestView(LocalizedView):
    """Базовий View для тестування"""
    test_type = None

    async def _get_public_tests(self, request):
        author_id = request.GET.get("author")
        page = request.GET.get("page", 1)

        if not author_id:
            category_list, level = categories_level_sort_present(request)
            test_data = await get_instance_cached_all("public test", "public_tests_get", category_list, level)
        else:
            test_data = await get_instance_cached_by_author_id("public test", "public_tests_get", author_id)

        if isinstance(test_data, JsonResponse):
            return test_data

        paged_data_dict = await sync_to_async(lambda: paginate_list(test_data, int(page), 24))()

        return success_response({
            "page": int(page),
            "total_tests": len(test_data),
            "total_pages": paged_data_dict["total_pages"],
            "tests": paged_data_dict["results"]
        })

    async def _get_test_by_id(self, test_type, test_id):
        cache_config = {
            "module": ("module test", "courses_get"),
            "course": ("course test", "courses_get"),
            "public": ("public test", "public_tests_get"),
        }
        if test_type not in cache_config:
            return error_response(gettext("Unsupported test type"), status=400)

        instance_type, cache_name = cache_config[test_type]
        return await get_cached_instance_by_id(instance_type, cache_name, test_id)

    @login_required_async
    async def get(self, request, test_id=None):
        if self.test_type == "public" and test_id is None:
            return await self._get_public_tests(request)
        elif test_id is not None:
            test = await self._get_test_by_id(self.test_type, test_id)
            return success_response(data=test, message=gettext("Test retrieved successfully"))
        return error_response(gettext("Invalid request"), status=400)

    @permission_test_required
    async def post(self, request):
        data = json.loads(request.POST.get("data", "{}"))
        data = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in data.items()}

        try:
            error = await validate_test_editable(self.test_type, data, "add")
            if error:
                return error

            test = await create_test(self.test_type, request.user, data)
            return success_response({
                "message": gettext("Test created successfully."),
                "test_type": self.test_type,
                "test_id": test.id
            })
        except (Course.DoesNotExist, Module.DoesNotExist) as e:
            return error_response(gettext(f"{str(e).split()[0]} not found"), status=404)
        except (ValidationError, ValueError) as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response(f"{gettext("Error creating test:")} {str(e)}", status=500)

    @permission_test_required
    async def patch(self, request, test_id):
        parsed_data, _, raw_form, parse_error = parse_multipart_request(request)
        if parse_error:
            return parse_error
        if not parsed_data:
            return error_response(gettext("No data provided for update"), status=400)

        all_new_questions_data = raw_form.get("all_new_questions_data", "false").lower()
        data = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in parsed_data.items()}

        try:
            uuid_obj = validate_uuid(test_id)
            return await update_test(data, uuid_obj, self.test_type, all_new_questions_data)
        except ValidationError as e:
            return error_response(str(e), status=400)
        except (Course.DoesNotExist, Module.DoesNotExist, Test.DoesNotExist) as e:
            return error_response(gettext(f"{str(e).split()[0]} not found"), status=404)
        except Exception as e:
            return error_response(f"{gettext('Test deletion error:')} {str(e)}", status=500)

    @permission_test_required
    async def delete(self, request, test_id):
        try:
            uuid_obj = validate_uuid(test_id)
            return await remove_test(uuid_obj, self.test_type)
        except ValidationError as e:
            return error_response(str(e), status=400)
        except (Course.DoesNotExist, Module.DoesNotExist, Test.DoesNotExist) as e:
            return error_response(gettext(f"{str(e).split()[0]} not found"), status=404)
        except Exception as e:
            return error_response(f"{gettext('Test deletion error:')} {str(e)}", status=500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ModuleTestView(BaseTestView):
    """View для тестів модуля"""
    test_type = "module"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseTestView(BaseTestView):
    """View для тестів курсу"""
    test_type = "course"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class PublicTestView(BaseTestView):
    """View для публічних тестів"""
    test_type = "public"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class TestAttemptView(LocalizedView):
    @login_required_async
    async def get(self, request, test_id):
        """Повертає:
        1. Історію спроб.
        2. Конфігурацію (чи можна проходити ще, чи показувати відповіді)."""
        user = request.user
        test_type = request.GET.get("test_type")

        if not test_type or test_type not in ["public", "course_test", "module_test"]:
            return error_response("Invalid or missing test type", status=400)

        return await history_and_config(test_id, user, test_type)

    @login_required_async
    async def post(self, request, test_id):
        """Спроба користувача пройти тест"""
        user_id = request.user.id

        try:
            body = json.loads(request.body)
            test_type = body.get('test_type')
            answers = body.get("answers")

            if not test_type or test_type not in ["public", "course_test", "module_test"]:
                return error_response("Invalid or missing test type", status=400)

            if not answers or not isinstance(answers, list):
                return error_response("Answers list are required", status=400)

            submit_test = await submit_test_attempt(user_id, test_id, test_type, answers)

            return success_response({
                "message": "Test submitted successfully",
                "result": submit_test
            })

        except ValidationError as e:
            return error_response(str(e), status=400)
        except ValueError as e:
            return error_response(str(e), status=400)
        except ObjectDoesNotExist:
            return error_response("Test or Enrollment not found", status=404)
        except Exception as e:
            return error_response(f"Error submitting test: {str(e)}", status=500)
