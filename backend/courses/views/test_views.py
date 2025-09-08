from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from courses.decorators import teacher_required, owner_public_test_required


@method_decorator(ensure_csrf_cookie, name="dispatch")
class TestViews(LocalizedView):
    """View для роботи з публічними тестуваннями"""

    @login_required_async
    async def get(self, request, course_id=None):
        """Отримання публічних тестів"""
        pass

    @login_required_async
    @teacher_required
    async def post(self, request):
        """Створення публічного тесту викладачем"""
        pass

    @login_required_async
    @owner_public_test_required
    async def patch(self, request, test_id):
        """Оновлення публічного тесту викладачем"""
        pass

    @login_required_async
    @owner_public_test_required
    async def delete(self, request, test_id):
        """Видалення публічного тесту викладачем"""
        pass
