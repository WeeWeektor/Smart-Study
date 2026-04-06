from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext

from .generate_activation_token import generate_activation_token


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
