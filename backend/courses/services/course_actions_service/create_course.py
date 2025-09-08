from asgiref.sync import sync_to_async

from courses.models import CourseMeta, Course
from courses.services import validate_course_data, upload_course_cover_image


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
    ))()

    if cover_file:
        await upload_course_cover_image(course_created, cover_file)

    if course_created.is_published:
        course_created.publish()

    return course_created
