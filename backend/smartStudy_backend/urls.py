from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from smartStudy_backend import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('silk/', include('silk.urls', namespace='silk')),
    path('api/auth/', include('users.auth_urls', namespace='auth_urls')),
    path('api/user/', include('users.user_urls', namespace='user_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
