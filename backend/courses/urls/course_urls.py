from django.urls import path

from courses.views import CourseView

app_name = 'course'
urlpatterns = [
    path('courses/', CourseView.as_view(), name='course-list'),
    path('course/<uuid:course_id>/', CourseView.as_view(), name='course-detail'),
]
