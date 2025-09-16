from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from courses.services.cache_service import invalidate_instance_cached_all


async def publish_course(course):
    """Публікація курсу власником курсу"""

    if not course.cover_image:
        raise ValidationError(_('Missing required field for publish: cover_image'))
    else:
        await sync_to_async(lambda: course.publish())()

        await sync_to_async(
            lambda: invalidate_instance_cached_all(
                instance_type="courses",
                instance_type_cache="courses_get",
                category=course.category,
                level=course.details.level,
                author_id=course.owner.id
            ),
            thread_sensitive=True
        )()
