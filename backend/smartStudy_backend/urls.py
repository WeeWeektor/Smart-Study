from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from smartStudy_backend import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('silk/', include('silk.urls', namespace='silk')),
    path('api/auth/', include('users.auth_urls', namespace='auth_urls')),
    path('api/user/', include('users.user_urls', namespace='user_urls')),
    path('api/user-calendar/', include('users_calendar.urls', namespace='user_calendar_urls')),
    path('api/notifications/', include('notifications.urls', namespace='notifications')),
    path('api/course/', include('courses.urls.course_urls', namespace='course_urls')),
    path('api/module/', include('courses.urls.module_urls', namespace='module_urls')),
    path('api/lesson/', include('courses.urls.lesson_urls', namespace='lesson_urls')),
    path('api/test/', include('courses.urls.test_urls', namespace='test_urls')),
    path('api/course-review/', include('courses.urls.course_review_urls', namespace='course_review')),
    path('api/wishlist/', include('courses.urls.wishlist_urls', namespace='wishlist_urls')),
    path('api/enrollment/', include('courses.urls.enrollment_urls', namespace='enrollment_urls')),
    path('api/choices/', include('courses.urls.choices_urls', namespace='choices_urls')),
    path('api/counter/', include('courses.urls.counter_urls', namespace='counter_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
