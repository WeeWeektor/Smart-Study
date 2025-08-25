from django.utils import translation

from smartStudy_backend import settings


class LocalizedMixin:
    @staticmethod
    def _set_language(request):
        lang = request.headers.get('Accept-Language')
        if lang not in dict(settings.LANGUAGES).keys():
            lang = 'en'
        translation.activate(lang)
        return lang

    def dispatch(self, request, *args, **kwargs):
        self._set_language(request)
        try:
            return super().dispatch(request, *args, **kwargs)
        finally:
            translation.deactivate()
