from django.utils.translation import gettext

from common.utils import send_template_email
from users.utils.email_templates import get_verification_email_plain, get_verification_email_html, \
    get_password_reset_email_html, get_password_reset_email_plain


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
