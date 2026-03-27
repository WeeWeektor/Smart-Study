from django.urls import path

from notifications.views import NotificationView

app_name = 'notifications'

urlpatterns = [
    path('get_notifications/', NotificationView.as_view(), name='get_notifications'),
    # path('mark_as_read/', )
]
