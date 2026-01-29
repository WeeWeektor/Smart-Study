from asgiref.sync import sync_to_async

from courses.models import CourseMeta
from courses.services.builder_json import build_course_json_success
from users.models import CustomUser


async def generate_course_json_with_details_and_owner(courses: list):
    course_ids = [c.id for c in courses if getattr(c, 'id', None)]
    owner_ids = [c.owner_id for c in courses if getattr(c, 'owner_id', None)]

    course_details = await sync_to_async(lambda: list(CourseMeta.objects.filter(course_id__in=course_ids)))()
    course_owners = await sync_to_async(lambda: list(CustomUser.objects.filter(id__in=owner_ids)))()

    details_map = {d.course_id: d for d in course_details}
    owners_map = {o.id: o for o in course_owners}

    course_data = []
    for c in courses:
        details = details_map.get(c.id)
        owner = owners_map.get(c.owner_id) if getattr(c, "owner_id", None) else None

        course_data.append(
            build_course_json_success(c, details, owner)
        )

    return course_data
