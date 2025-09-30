from django.urls import path
from .views import ProfileView, ChangePasswordView, UserInfoView


app_name = 'user'
urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/upload-avatar/", ProfileView.as_view(), name="upload-avatar"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("user-info/<uuid:user_id>/", UserInfoView.as_view(), name="user-info"),
]
