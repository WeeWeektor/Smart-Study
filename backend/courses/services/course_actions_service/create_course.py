from asgiref.sync import sync_to_async

from common.services import mongo_repo
from common.utils import validate_uuid
from courses.models import CourseMeta, Course
from courses.services import validate_course_data
from courses.services.cache_service import invalidate_instance_cached_all
from courses.services.course_actions_service import upload_course_cover_image


async def create_course(user, data, cover_file=None):
    uuid_obj = validate_uuid(user.id)
    validate_course_data(data)

    structure_ids = await sync_to_async(mongo_repo.insert_document)("course_structures", {})

    course_created = await sync_to_async(Course.objects.create)(
        title=data["title"].strip(),
        description=data["description"].strip(),
        category=data["category"],
        owner_id=uuid_obj,
        structure_ids=structure_ids
    )
    await sync_to_async(CourseMeta.objects.create)(
        course=course_created,
        level=data.get("level"),
        course_language=data.get("course_language"),
        time_to_complete=data.get("time_to_complete"),
    )

    if cover_file:
        await upload_course_cover_image(course_created, cover_file)

    await sync_to_async(
        lambda: invalidate_instance_cached_all(
            instance_type="courses",
            instance_type_cache="courses_get",
            category=course_created.category,
            level=course_created.details.level,
            author_id=str(course_created.owner_id)
        ),
        thread_sensitive=True
    )()

    return course_created


async def count_content_course(data, course_created):
    if data.get("is_published") is True:
        from courses.services.course_actions_service import publish_course
        await publish_course(course_created)
    else:
        from courses.services.course_actions_service import count_content
        await count_content(course_created)
