from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from smartStudy_backend import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('silk/', include('silk.urls', namespace='silk')),
    path('api/auth/', include('users.auth_urls', namespace='auth_urls')),
    path('api/user/', include('users.user_urls', namespace='user_urls')),
    path('api/course/', include('courses.urls.course_urls', namespace='course_urls')),
    path('api/module/', include('courses.urls.module_urls', namespace='module_urls')),
    path('api/test/', include('courses.urls.test_urls', namespace='test_urls')),
    path('api/choices/', include('courses.urls.choices_urls', namespace='choices_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
