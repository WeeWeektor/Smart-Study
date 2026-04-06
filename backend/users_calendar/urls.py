from django.urls import path

from users_calendar.views import PersonalEventListCreateView, PersonalEventDetailView, CoursePlaningListCreateView, CoursePlaningDetailView

app_name = 'user_calendar'

urlpatterns = [
    path('personal-events/', PersonalEventListCreateView.as_view(), name='event_list_create'),
    path('personal-events/<uuid:pk>/', PersonalEventDetailView.as_view(), name='event_detail'),

    path('course-events/', CoursePlaningListCreateView.as_view(), name='course_event_list_create'),
    path('course-events/<uuid:pk>/', CoursePlaningDetailView.as_view(), name='course_event_detail'),
]
