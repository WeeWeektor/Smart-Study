from django.utils import translation

from smartStudy_backend import settings


class LocalizedMixin:
    def dispatch(self, request, *args, **kwargs):
        lang = request.headers.get('Accept-Language')
        if lang not in dict(settings.LANGUAGES).keys():
            lang = 'en'
        translation.activate(lang)
        try:
            return super().dispatch(request, *args, **kwargs)
        finally:
            translation.deactivate()
