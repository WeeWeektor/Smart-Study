from django.urls import path

from courses.views import LessonView

app_name = 'lesson'
urlpatterns = [
    path('create-lesson/', LessonView.as_view(), name='create-lesson'),
    path('lesson/<uuid:lesson_id>/', LessonView.as_view(), name='get-lesson'),
    path('delete-lesson/<uuid:lesson_id>/', LessonView.as_view(), name='delete-lesson'),
    path('change-lesson/<uuid:lesson_id>/', LessonView.as_view(), name='change-lesson'),
]
