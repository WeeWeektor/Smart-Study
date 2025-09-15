from asgiref.sync import sync_to_async

from courses.models import CourseMeta, Course
from courses.services import validate_course_data, upload_course_cover_image


async def create_course(user, data, cover_file=None):
    validate_course_data(data)

    course_created = await sync_to_async(Course.objects.create)(
        title=data["title"].strip(),
        description=data["description"].strip(),
        category=data["category"],
        owner_id=user.id,
    )
    await sync_to_async(CourseMeta.objects.create)(
        course=course_created,
        level=data.get("level"),
        course_language=data.get("course_language"),
        time_to_complete=data.get("time_to_complete"),
    )

    if cover_file:
        await upload_course_cover_image(course_created, cover_file)

    if data.get("is_published") is True:
        from courses.services import publish_course
        await publish_course(course_created)

    return course_created
