from courses.views.certificate_views import CertificateView, DownloadCertificateView, VerifyCertificateView
from courses.views.choices_views import ChoicesView
from courses.views.counter_views import CountAllPublishedCourses, CountTeacherCourses
from courses.views.course_recommendations_views import CourseRecommendationsView
from courses.views.course_review_views import CourseReviewView
from courses.views.course_views import CourseView, PublishCourseView
from courses.views.courses_by_user_views import CoursesByUserView
from courses.views.lesson_views import LessonView
from courses.views.module_views import ModuleView
from courses.views.test_views import CourseTestView, ModuleTestView, PublicTestView, TestAttemptView
from courses.views.user_course_enrollment_views import UserCourseEnrollmentView, UserCourseEnrollmentStatusView, \
    CourseTestResultsView
from courses.views.user_wishlist_views import UserWishlistView

__all__ = [
    "UserCourseEnrollmentStatusView",
    "CertificateView",
    "DownloadCertificateView",
    "VerifyCertificateView",
    "CourseTestResultsView",
    "CourseView",
    "CourseRecommendationsView",
    "PublishCourseView",
    "ModuleView",
    "ModuleTestView",
    "CourseTestView",
    "PublicTestView",
    "TestAttemptView",
    "LessonView",
    "ChoicesView",
    "CountAllPublishedCourses",
    "CountTeacherCourses",
    "CourseReviewView",
    "UserWishlistView",
    "CoursesByUserView",
    "UserCourseEnrollmentView",
]
