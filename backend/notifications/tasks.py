from celery import shared_task
from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@shared_task(name='notifications.tasks.send_bulk_notification_email_task')
def send_bulk_notification_email_task(recipient_list, title, message, personal_link=None, link_text=None):
    context = {
        'title': title,
        'message': message,
        'personal_link': personal_link,
        'link_text': link_text,
    }

    html_message = render_to_string('emails/notification_template.html', context)
    plain_message = strip_tags(html_message)

    CHUNK_SIZE = 50

    try:
        with get_connection() as connection:
            for i in range(0, len(recipient_list), CHUNK_SIZE):
                chunk = recipient_list[i: i + CHUNK_SIZE]
                messages = []

                for email in chunk:
                    mail = EmailMultiAlternatives(
                        subject=title,
                        body=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email],
                        connection=connection
                    )
                    mail.attach_alternative(html_message, "text/html")
                    messages.append(mail)

                connection.send_messages(messages)

    except Exception as exc:
        print(f"Failed to send bulk emails: {exc}")
