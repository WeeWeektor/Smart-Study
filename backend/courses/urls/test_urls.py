from django.urls import path

from courses.views import CourseTestView, ModuleTestView, PublicTestView

app_name = 'test'
urlpatterns = [
    path('test_course/<uuid:test_id>/', CourseTestView.as_view(), name='test-course-detail'),
    path('test_module/<uuid:test_id>/', ModuleTestView.as_view(), name='test-module-detail'),
    path('public_test/<uuid:test_id>/', PublicTestView.as_view(), name='public-test-detail'),
    path('public_tests/', PublicTestView.as_view(), name='public-test-list'),
]
