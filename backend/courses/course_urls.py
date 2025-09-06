from django.urls import path

from courses.views import CourseView

app_name = 'course'
urlpatterns = [
    # Course endpoints
    path('courses/', CourseView.as_view(), name='course-list'),
    path('courses/<uuid:pk>/', CourseView.as_view(), name='course-detail'),
]
