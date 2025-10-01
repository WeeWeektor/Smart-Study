from courses.views.course_views import CourseView
from courses.views.module_views import ModuleView
from courses.views.test_views import CourseTestView, ModuleTestView, PublicTestView
from courses.views.choices_views import ChoicesView
from courses.views.counter_views import CountAllPublishedCourses, CountTeacherCourses

__all__ = [
    "CourseView",
    "ModuleView",
    "ModuleTestView",
    "CourseTestView",
    "PublicTestView",
    "ChoicesView",
    "CountAllPublishedCourses",
    "CountTeacherCourses",
]
