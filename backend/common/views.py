import asyncio

from asgiref.sync import sync_to_async
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import translation

from common.mixins import LocalizedMixin


class LocalizedView(LocalizedMixin, View):
    async def dispatch(self, request, *args, **kwargs):
        self._set_language(request)
        try:
            handler = getattr(self, request.method.lower(), None)
            if handler and asyncio.iscoroutinefunction(handler):
                response = await handler(request, *args, **kwargs)
                return response
            else:
                dispatch_sync = sync_to_async(super().dispatch)
                response = await dispatch_sync(request, *args, **kwargs)
                return response
        finally:
            translation.deactivate()

class LocalizedAPIView(LocalizedMixin, APIView):
    async def dispatch(self, request, *args, **kwargs):
        self._set_language(request)
        try:
            handler = getattr(self, request.method.lower(), None)
            if handler and asyncio.iscoroutinefunction(handler):
                response = await handler(request, *args, **kwargs)
                if isinstance(response, Response):
                    response.request = request
                return response
            else:
                dispatch_sync = sync_to_async(super().dispatch)
                response = await dispatch_sync(request, *args, **kwargs)
                return response
        finally:
            translation.deactivate()
