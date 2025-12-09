from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


async def publish_course(course):
    """Публікація курсу власником курсу"""

    if not course.cover_image:
        raise ValidationError(_('Missing required field for publish: cover_image'))
    else:
        await sync_to_async(lambda: course.publish())()


async def count_content(course):
    """Підрахунок контенту курсу перед публікацією"""
    await sync_to_async(lambda: course.count_content_without_publish())()
