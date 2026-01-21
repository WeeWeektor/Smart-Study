from asgiref.sync import sync_to_async

from courses.models import CourseMeta
from courses.services.builder_json import build_course_json_success
from users.models import CustomUser


async def generate_course_json_with_details_and_owner(courses: list):
    details_ids = [c.details.id for c in courses if getattr(c, 'details', None)]
    owner_ids = [c.owner.id for c in courses if getattr(c, 'owner', None)]

    course_details = await sync_to_async(lambda: list(CourseMeta.objects.filter(id__in=details_ids)))()
    course_owners = await sync_to_async(lambda: list(CustomUser.objects.filter(id__in=owner_ids)))()

    details_map = {d.id: d for d in course_details}
    owners_map = {o.id: o for o in course_owners}

    course_data = []
    for c in courses:
        details = details_map.get(c.details.id) if getattr(c, "details", None) else None
        owner = owners_map.get(c.owner.id) if getattr(c, "owner", None) else None

        course_data.append(
            build_course_json_success(c, details, owner)
        )

    return course_data
