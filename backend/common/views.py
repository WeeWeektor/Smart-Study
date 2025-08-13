from django.views import View
from rest_framework.views import APIView

from common.mixins import LocalizedMixin


class LocalizedView(LocalizedMixin, View):
    pass

class LocalizedAPIView(LocalizedMixin, APIView):
    pass
