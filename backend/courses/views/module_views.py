import json

from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.utils import sanitize_input, error_response, success_response
from courses.decorators import permission_module_required
from courses.services.module_actons_service import create_module


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ModuleView(LocalizedView):
    @permission_module_required
    async def post(self, request):
        data = json.loads(request.POST.get('data', '{}'))
        data = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in data.items()}

        try:
            module = await create_module(data, data.get("course_id"))
            return success_response({
                "message": gettext("Module created successfully."),
                "module": str(module.id)
            })
        except ValidationError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response(f"{gettext("Error creating module:")} {str(e)}", status=500)

    @permission_module_required
    async def patch(self, request, module_id):
        pass

    @permission_module_required
    async def delete(self, request, module_id):
        pass

# Отримання модулю буде метод в services/module_action_service але не буде вьюхою
# Отримання модулю буде використовуватись в курсі для отримання повної структури курсу
# При створенні модуля додавати в структуру курсу дані модуля
#
# в mongo буде зберігатись структура модулю по типу:
# {
#   "_id"
#   counter: int
#   structure: [
#    tupes: "lesson" | "test"
#    lesson_id | test_id
#    title
#    order
#   ]
#
#
#
