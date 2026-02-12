from django.urls import path

from courses.views import CourseView, CoursesByUserView, PublishCourseView, CertificateView, DownloadCertificateView, \
    CourseRecommendationsView

app_name = 'course'
urlpatterns = [
    path('courses-list/', CourseView.as_view(), name='course-list'),
    path('courses-list/<str:search_query>/', CourseView.as_view(), name='course-list-search'),
    path('get-user-course/', CoursesByUserView.as_view(), name='get-user-courses'),
    path('create-course/', CourseView.as_view(), name='create-course'),
    path('delete-course/<uuid:course_id>/', CourseView.as_view(), name='delete-course'),
    path('change-course/<uuid:course_id>/', CourseView.as_view(), name='change-course'),
    path('course/<uuid:course_id>/', CourseView.as_view(), name='course-detail'),

    path('publish-course/<uuid:course_id>/', PublishCourseView.as_view(), name='publish-course'),

    path('create-certificate/<uuid:course_id>/', CertificateView.as_view(), name='create-certificate'),
    path('download-certificate/<str:certificate_id>/', DownloadCertificateView.as_view(), name='download-certificate'),

    path('course-recommendations/<uuid:course_id>/', CourseRecommendationsView.as_view(),
         name='course-recommendations'),
]
