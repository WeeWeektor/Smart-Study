from django.urls import path

from courses.views import CourseTestView, ModuleTestView, PublicTestView, TestAttemptView

app_name = 'test'
urlpatterns = [
    # URLs for public tests
    path('public-tests-list/', PublicTestView.as_view(), name='public-test-list'),
    path('create-public-test/', PublicTestView.as_view(), name='create-public-test'),
    path('delete-public-test/<uuid:test_id>/', PublicTestView.as_view(), name='delete-public-test'),
    path('change-public-test/<uuid:test_id>/', PublicTestView.as_view(), name='change-public-test'),
    path('pablic-test/<uuid:test_id>/', PublicTestView.as_view(), name='public-test-detail'),

    # URLs for course tests
    path('course-test/<uuid:test_id>/', CourseTestView.as_view(), name='course-test-detail'),
    path('create-course-test/', CourseTestView.as_view(), name='create-course-test'),
    path('delete-course-test/<uuid:test_id>/', CourseTestView.as_view(), name='delete-course-test'),
    path('change-course-test/<uuid:test_id>/', CourseTestView.as_view(), name='change-course-test'),

    # URLs for module tests
    path('module-test/<uuid:test_id>/', ModuleTestView.as_view(), name='module-test-detail'),
    path('create-module-test/', ModuleTestView.as_view(), name='create-module-test'),
    path('delete-module-test/<uuid:test_id>/', ModuleTestView.as_view(), name='delete-module-test'),
    path('change-module-test/<uuid:test_id>/', ModuleTestView.as_view(), name='change-module-test'),

    # URL for test attempts
    path('get-history-test-attempts/<uuid:test_id>/', TestAttemptView.as_view(), name='get-history-test-attempts'),
    path('start-test-attempt/<uuid:test_id>/', TestAttemptView.as_view(), name='start-test-attempt'),
]
