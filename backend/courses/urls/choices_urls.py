from django.urls import path

from courses.views import ChoicesView

app_name = 'choices'
urlpatterns = [
    path('choices-get/', ChoicesView.as_view(), name='choices-get'),
]
