from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from courses.models import CourseMeta, Course
from courses.services import validate_course_data, upload_course_cover_image


async def create_course(user, data, cover_file=None):
    validate_course_data(data)

    course_created = await sync_to_async(lambda: Course.objects.create(
        title=data["title"].strip(),
        description=data["description"].strip(),
        category=data["category"],
        owner_id=user.id,
    ))()
    await sync_to_async(lambda: CourseMeta.objects.create(
        course=course_created,
        level=data.get("level"),
        course_language=data.get("course_language"),
        time_to_complete=data.get("time_to_complete"),
    ))()

    if cover_file:
        await upload_course_cover_image(course_created, cover_file)

    if data.get("is_published") is True:
        if not course_created.cover_image:
            raise ValidationError(_('Missing required field for publish: cover_image'))
        else:
            await sync_to_async(lambda: course_created.publish())()

            from courses.services import invalidate_instance_cached_all
            await invalidate_instance_cached_all(instance_type="courses",
                                                 instance_type_cache="courses_get",
                                                 category=data.get("category"),
                                                 level=data.get("level"),
                                                 author_id=str(user.id)
                                                 )

    return course_created
