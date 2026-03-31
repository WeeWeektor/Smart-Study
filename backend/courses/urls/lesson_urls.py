from django.urls import path

from courses.views import LessonView

app_name = 'lesson'
urlpatterns = [
    path('lesson/<uuid:lesson_id>/', LessonView.as_view(), name='get-lesson'),
]
