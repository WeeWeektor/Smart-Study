from django.urls import path

from courses.views import CourseView, CourseStructureView

app_name = 'course'
urlpatterns = [
    path('courses-list/', CourseView.as_view(), name='course-list'),
    path('courses-list/<str:search_query>/', CourseView.as_view(), name='course-list-search'),
    path('create-course/', CourseView.as_view(), name='create-course'),
    path('delete-course/<uuid:course_id>/', CourseView.as_view(), name='delete-course'),
    path('change-course/<uuid:course_id>/', CourseView.as_view(), name='change-course'),
    path('course/<uuid:course_id>/', CourseView.as_view(), name='course-detail'),
    path('course-structure/<uuid:course_id>/', CourseStructureView.as_view(), name='course-structure')
]
