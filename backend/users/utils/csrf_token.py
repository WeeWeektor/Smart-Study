from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie

@method_decorator(ensure_csrf_cookie, name="dispatch")
class CSRFTokenView(View):
    @staticmethod
    def get(request):
        return JsonResponse({'success': gettext('CSRF cookie set')})
