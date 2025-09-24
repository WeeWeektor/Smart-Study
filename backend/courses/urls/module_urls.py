from django.urls import path

from courses.views import ModuleView

app_name = 'module'
urlpatterns = [
    path('create-module/', ModuleView.as_view(), name='create-module'),
    path('delete-module/<uuid:course_id>/', ModuleView.as_view(), name='delete-module'),
    path('change-module/<uuid:course_id>/', ModuleView.as_view(), name='change-module'),
]
