from django.urls import path

from courses.views import CourseReviewView

app_name = 'course_review'
urlpatterns = [
    path('create-review/', CourseReviewView.as_view(), name='create-review'),
    path('get_reviews/', CourseReviewView.as_view(), name='get-reviews'),
]
