from courses.views.course_review_views import CourseReviewView
from courses.views.course_views import CourseView, PublishCourseView
from courses.views.lesson_views import LessonView
from courses.views.module_views import ModuleView
from courses.views.test_views import CourseTestView, ModuleTestView, PublicTestView
from courses.views.choices_views import ChoicesView
from courses.views.counter_views import CountAllPublishedCourses, CountTeacherCourses
from courses.views.user_wishlist_views import UserWishlistView
from courses.views.courses_by_user_views import CoursesByUserView

__all__ = [
    "CourseView",
    "PublishCourseView",
    "ModuleView",
    "ModuleTestView",
    "CourseTestView",
    "PublicTestView",
    "LessonView",
    "ChoicesView",
    "CountAllPublishedCourses",
    "CountTeacherCourses",
    "CourseReviewView",
    "UserWishlistView",
    "CoursesByUserView",
]
