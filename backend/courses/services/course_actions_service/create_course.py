from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from courses.models import CourseMeta, Course
from courses.services import validate_course_data, upload_course_cover_image, invalidate_instance_cached_by_author_id
from courses.services.cache_service.category_level_all_for_instance_cache import invalidate_instance_cached_all


async def create_course(user, data, cover_file=None):
    validate_course_data(data)

    course_created = await sync_to_async(lambda: Course.objects.create(
        title=data["title"].strip(),
        description=data["description"].strip(),
        category=data["category"],
        owner_id=user.id,
        is_published=data.get("is_published", False),
    ))()
    await sync_to_async(lambda: CourseMeta.objects.create(
        course=course_created,
        level=data.get("level"),
        course_language=data.get("course_language"),
        time_to_complete=data.get("time_to_complete"),
    ))()

    print(cover_file)

    if cover_file:
        await upload_course_cover_image(course_created, cover_file)

    if course_created.is_published:
        if not data.get("cover_image"):
            raise ValidationError(_('Missing required field for publish: cover_image'))
        else:
            await sync_to_async(lambda: course_created.publish())()

            await sync_to_async(lambda: invalidate_instance_cached_by_author_id("courses", "courses", str(user.id)))()
            await sync_to_async(lambda: invalidate_instance_cached_all("courses", "courses", None, data.get("level")))()
            await sync_to_async(lambda: invalidate_instance_cached_all("courses", "courses", None, None))()
            await sync_to_async(lambda: invalidate_instance_cached_all("courses", "courses", data.get("category"), None))()
            await sync_to_async(
                lambda: invalidate_instance_cached_all("courses", "courses", data.get("category"), data.get("level")))()

    return course_created
