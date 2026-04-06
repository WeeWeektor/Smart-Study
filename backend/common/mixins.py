import asyncio
from asgiref.sync import sync_to_async
from django.utils import translation
from rest_framework.response import Response

from common.utils import get_language_from_request, validate_language


class LocalizedMixin:
    @staticmethod
    def _set_language(request):
        lang = get_language_from_request(request)
        lang = validate_language(lang)
        translation.activate(lang)
        return lang

    def dispatch(self, request, *args, **kwargs):
        """Synchronous dispatch for regular Views"""
        self._set_language(request)
        try:
            return super().dispatch(request, *args, **kwargs)
        finally:
            translation.deactivate()

    async def async_dispatch(self, request, *args, **kwargs):
        """Asynchronous dispatch for async Views and APIViews"""
        self._set_language(request)
        try:
            handler = getattr(self, request.method.lower(), None)
            if handler and asyncio.iscoroutinefunction(handler):
                response = await handler(request, *args, **kwargs)
                if hasattr(self, 'finalize_response') and isinstance(response, Response):
                    response.request = request
                return response
            else:
                dispatch_sync = sync_to_async(super().dispatch)
                response = await dispatch_sync(request, *args, **kwargs)
                return response
        finally:
            translation.deactivate()
