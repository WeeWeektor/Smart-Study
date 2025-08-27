from django.views import View
from rest_framework.views import APIView

from common.mixins import LocalizedMixin


class LocalizedView(LocalizedMixin, View):
    async def dispatch(self, request, *args, **kwargs):
        return await self.async_dispatch(request, *args, **kwargs)

class LocalizedAPIView(LocalizedMixin, APIView):
    async def dispatch(self, request, *args, **kwargs):
        return await self.async_dispatch(request, *args, **kwargs)
