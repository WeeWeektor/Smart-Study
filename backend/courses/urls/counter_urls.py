from django.urls import path

from courses.views import CountAllPublishedCourses, CountTeacherCourses

app_name = 'counter'
urlpatterns = [
    path('all-published-courses/', CountAllPublishedCourses.as_view(), name='get-count-all-published-courses'),
    path('teacher-courses/', CountTeacherCourses.as_view(), name='get-count-teacher-courses'),
]
