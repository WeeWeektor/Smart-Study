import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.translation import gettext

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import success_response, paginate_list, sanitize_input, error_response
from courses.decorators import teacher_required, owner_public_test_required
from courses.services.cache_service import get_instance_cached_all, get_instance_cached_by_author_id, \
    get_cached_instance_by_id
from courses.services.test_actions_service import create_test
from courses.utils import categories_level_present


class BaseTestView(LocalizedView):
    """Базовий View для тестування"""
    test_type = None

    async def _get_public_tests(self, request):
        author_id = request.GET.get("author")
        page = request.GET.get("page", 1)

        if not author_id:
            category_list, level = categories_level_present(request)
            test_data = await get_instance_cached_all("tests", "public_tests_get", category_list, level)
        else:
            test_data = await get_instance_cached_by_author_id("tests", "public_tests_get", author_id)

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
        test_data = await get_cached_instance_by_id(instance_type, cache_name, test_id)
        return success_response(test_data)

    @login_required_async
    async def get(self, request, test_id=None):
        if self.test_type == "public" and test_id is None:
            return await self._get_public_tests(request)
        elif test_id is not None:
            return await self._get_test_by_id(self.test_type, test_id)
        return error_response(gettext("Invalid request"), status=400)

    @login_required_async
    @teacher_required
    async def post(self, request):
        data = json.loads(request.POST.get("data", "{}"))
        data = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in data.items()}

        try:
            test = await create_test(self.test_type, request.user, data, self.test_type)
            return success_response({
                "message": gettext("Test created successfully."),
                "test_type": self.test_type,
                "test_id": test.id
            })
        except ValidationError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response(f"{gettext("Error creating test:")} {str(e)}", status=500)

    @login_required_async
    @owner_public_test_required  #  TODO створити декоратори для course і module тестів
    async def patch(self, request, test_id):
        pass

    @login_required_async
    @owner_public_test_required
    async def delete(self, request, test_id):
        pass


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ModuleTestView(BaseTestView):
    """View для тестів модулля"""
    test_type = "module"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseTestView(BaseTestView):
    """View для тестів курсу"""
    test_type = "course"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class PublicTestView(BaseTestView):
    """View для публічних тестів"""
    test_type = "public"
