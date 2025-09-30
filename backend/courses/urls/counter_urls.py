from django.urls import path

from courses.views import CountAllPublishedCourses

app_name = 'counter'
urlpatterns = [
    path('all-published-courses/', CountAllPublishedCourses.as_view(), name='get-count-all-published-courses'),
]
