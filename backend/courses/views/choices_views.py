from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from courses.choices import LEVELS, CATEGORY_CHOICES


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ChoicesView(LocalizedView):
    @login_required_async
    async def get(self, request):
        return JsonResponse({
            'levels': [dict(LEVELS)],
            'category': [dict(CATEGORY_CHOICES)],
        })
