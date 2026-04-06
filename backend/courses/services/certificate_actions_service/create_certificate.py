from common.utils import validate_uuid
from courses.models import Certificate


async def create_certificate(course_id, user_id):
    course_id = validate_uuid(course_id)
    user_id = validate_uuid(user_id)

    certificate, created = await Certificate.objects.aget_or_create(
        user_id=user_id,
        course_id=course_id
    )

    if created:
        from courses.services.cache_service import invalidate_course_enrollment_status_cache
        await invalidate_course_enrollment_status_cache(course_id, user_id)

    return certificate, created
