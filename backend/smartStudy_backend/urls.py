from django.contrib import admin
from django.urls import path, include

from smartStudy_backend import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.auth_urls', namespace='auth_urls')),
    path('api/user/', include('users.user_urls', namespace='user_urls')),
    ]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
