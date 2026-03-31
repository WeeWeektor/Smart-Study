from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from smartStudy_backend import settings


@shared_task
def send_bulk_notification_email_task(recipient_list, title, message, personal_link=None, link_text=None):
    context = {
        'title': title,
        'message': message,
        'personal_link': personal_link,
        'link_text': link_text,
    }

    html_message = render_to_string('emails/notification_template.html', context)
    plain_message = strip_tags(html_message)

    for email in recipient_list:
        try:
            send_mail(
                subject=title,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email to {email}: {str(e)}")
