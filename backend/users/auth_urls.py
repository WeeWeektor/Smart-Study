from django.urls import path
from .views import RegisterView, LoginView, VerifyEmailView, LogoutView, ForgotPasswordView, ResetPasswordView, \
    GoogleAuthView
from .utils.csrf_token import CSRFTokenView


app_name = 'auth'
urlpatterns = [
    path("get-csrf-token/", CSRFTokenView.as_view(), name='get-csrf-token'),
    path("register/", RegisterView.as_view(), name="registration"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("login/", LoginView.as_view(), name="login"),
    path('google-oauth/', GoogleAuthView.as_view(), name='google-oauth'),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
