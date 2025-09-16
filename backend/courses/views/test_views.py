from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import validate_uuid, error_response, success_response
from courses.decorators import teacher_required, owner_public_test_required
from courses.models import Test
from courses.utils import categories_level_present


class BaseTestView(LocalizedView):
    """Базовий View для тестування"""
    test_type = None

    @login_required_async
    async def get(self, request, test_id=None):
        try:
            # add test filter from author id
            if self.test_type == "public" and test_id is None:
                filter_list = categories_level_present(request)
                # tests_data = await get_cached_all_tests(is_public=True, filt=filter_list)
                # return success_response({"tests": tests_data})
                pass

            elif test_id is not None:
                uuid_obj = validate_uuid(test_id)

                if self.test_type == "module":
                    # Логіка для тестів модулів
                    pass
                elif self.test_type == "course":
                    # Логіка для тестів курсів
                    pass
                elif self.test_type == "public":
                    # Логіка для публічних тестів
                    pass

        except ValidationError as e:
            return error_response(str(e), status=400)
        except Test.DoesNotExist:
            return error_response("Test not found", status=404)
        except Exception as e:
            return error_response(f"Error retrieving test: {str(e)}", status=500)

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
