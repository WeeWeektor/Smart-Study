from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from common.utils import validate_uuid
from courses.models import Course


async def publish_course(course):
    """Публікація курсу власником курсу"""

    if not course.cover_image:
        raise ValidationError(_('Missing required field for publish: cover_image'))
    else:
        await sync_to_async(lambda: course.publish())()


async def count_content(course):
    """Підрахунок контенту курсу перед публікацією"""
    await sync_to_async(lambda: course.count_content_without_publish())()


async def publishing_course(course_id):
    course_id = validate_uuid(course_id)

    course = await sync_to_async(Course.objects.get)(pk=course_id)

    from courses.services.course_actions_service import count_content_course
    await count_content_course({"is_published": True}, course)

    from courses.services.cache_service import invalidate_instance_cached_all
    await sync_to_async(
        lambda: invalidate_instance_cached_all(
            instance_type="courses",
            instance_type_cache="courses_get",
            category=course.category,
            level=course.details.level,
            author_id=str(course.owner_id)
        ),
        thread_sensitive=True
    )()
