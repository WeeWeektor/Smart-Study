from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import success_response, paginate_list
from courses.decorators import teacher_required, owner_public_test_required
from courses.services.cache_service import get_instance_cached_all, get_instance_cached_by_author_id, \
    get_cached_instance_by_id
from courses.utils import categories_level_present


class BaseTestView(LocalizedView):
    """Базовий View для тестування"""
    test_type = None

    @login_required_async
    async def get(self, request, test_id=None):
        if self.test_type == "public" and test_id is None:
            author_id = request.GET.get("author")
            page = request.Get.get("page", 1)

            if not author_id:
                category_list, level = categories_level_present(request)
                public_test_data = await get_instance_cached_all("tests", "public_tests_get", category_list, level)
            else:
                public_test_data = await get_instance_cached_by_author_id("tests", "public_tests_get", author_id)

            if isinstance(public_test_data, JsonResponse):
                return public_test_data

            paged_data_dict = await sync_to_async(lambda: paginate_list(public_test_data, int(page), 24))()

            return success_response({
                "page": int(page),
                "total_tests": len(public_test_data),
                "total_pages": paged_data_dict["total_pages"],
                "tests": paged_data_dict["results"]
            })

        elif test_id is not None:
            if self.test_type == "module":
                module_test_data = await get_cached_instance_by_id("module test", "courses_get", test_id)
                return success_response(module_test_data)
            elif self.test_type == "course":
                course_test_data = await get_cached_instance_by_id("course test", "courses_get", test_id)
                return success_response(course_test_data)
            elif self.test_type == "public":
                public_test_data = await get_cached_instance_by_id("public test", "public_tests_get", test_id)
                return success_response(public_test_data)

    @login_required_async
    @teacher_required
    async def post(self, request):
        pass

    @login_required_async
    @owner_public_test_required
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
