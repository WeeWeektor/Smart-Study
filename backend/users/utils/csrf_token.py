from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CSRFTokenView(View):
    @staticmethod
    def get(request):
        csrf_token = get_token(request)
        return JsonResponse({'success': gettext('CSRF cookie set'), 'csrf_token': csrf_token})
