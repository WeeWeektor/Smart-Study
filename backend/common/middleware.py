from django.utils import translation

from common.utils import get_language_from_request, validate_language
from smartStudy_backend import settings


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = get_language_from_request(request)
        language = validate_language(language)

        translation.activate(language)
        request.LANGUAGE_CODE = language

        response = self.get_response(request)

        response.set_cookie(
            'django_language',
            language,
            max_age=365 * 24 * 60 * 60,
            httponly=False,
            samesite='Lax',
            secure=settings.SESSION_COOKIE_SECURE,
            path='/',
        )

        response['X-Current-Language'] = language

        translation.deactivate()
        return response
