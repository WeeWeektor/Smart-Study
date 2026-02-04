from django.urls import path

from courses.views import UserCourseEnrollmentView, UserCourseEnrollmentStatusView

app_name = 'enrollment'
urlpatterns = [
    path('get-enrollment-status/<uuid:course_id>/', UserCourseEnrollmentStatusView.as_view(),
         name='get-enrollment-status'),

    path('enrollment-course/<uuid:course_id>/', UserCourseEnrollmentView.as_view(), name='enrollment-course'),
    path('start-course-enrollment/<uuid:course_id>/', UserCourseEnrollmentView.as_view(),
         name='start-course-enrollment'),
    path('update-enrollment-progress/<uuid:course_id>/', UserCourseEnrollmentView.as_view(),
         name='update-enrollment-progress'),
]
