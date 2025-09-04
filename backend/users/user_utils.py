from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.signing import TimestampSigner
from django.http import JsonResponse
from django.utils.translation import gettext
from supabase import create_client, Client

from users.utils.email_templates import get_verification_email_plain, get_verification_email_html, \
    get_password_reset_email_html, get_password_reset_email_plain

signer = TimestampSigner()

supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_API_KEY
)


def error_response(message, status=400):
    return JsonResponse({"status": "error", "message": message}, status=status)


def success_response(data=None, message=gettext('Successfully')):
    response = {"status": "success", "message": message}
    if data:
        response.update(data)
    return JsonResponse(response)


def generate_activation_token(email):
    return signer.sign(email)


async def send_template_email(user, subject, url_path, html_template_func, plain_template_func):
    token = generate_activation_token(user.email)
    if not token:
        raise ValueError(gettext("Unable to create activation token."))

    base_url = getattr(settings, 'BASE_URL', 'https://127.0.0.1:8000')
    full_url = f"{base_url}{url_path}?token={token}"
    greeting = f"{gettext("Congratulations,")} {user.name}!" if user.name else gettext("Congratulations!")

    html_message = html_template_func(greeting, full_url)
    plain_message = plain_template_func(greeting, full_url)

    await sync_to_async(send_mail)(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


async def send_verification_email(user):
    await send_template_email(
        user=user,
        subject=gettext("Email confirmation for SmartStudy"),
        url_path="/api/auth/verify-email/",
        html_template_func=get_verification_email_html,
        plain_template_func=get_verification_email_plain
    )


async def send_password_reset_email(user):
    await send_template_email(
        user=user,
        subject=gettext("Password recovery for SmartStudy"),
        url_path="/api/auth/reset-password/",
        html_template_func=get_password_reset_email_html,
        plain_template_func=get_password_reset_email_plain
    )
