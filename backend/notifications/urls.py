from django.urls import path

from notifications.views import NotificationView, MarkNotificationsAsReadView, CourseAnnouncementView

app_name = 'notifications'

urlpatterns = [
    path('get_notifications/', NotificationView.as_view(), name='get_notifications'),

    path('mark_as_read/', MarkNotificationsAsReadView.as_view(), name='mark_as_read'),

    path('get_owner_course_notifications/<str:course_id>/', CourseAnnouncementView.as_view(),
         name='get_owner_course_notifications'),
    path('post_owner_course_notifications/<str:course_id>/', CourseAnnouncementView.as_view(),
         name='post_owner_course_notifications'),
]
