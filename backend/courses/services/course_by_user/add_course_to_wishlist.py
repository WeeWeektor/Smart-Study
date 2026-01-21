from asgiref.sync import sync_to_async

from common.utils import validate_uuid
from courses.models import Wishlist


async def add_course_to_wishlist(user_id, course_id):
    user_id = validate_uuid(user_id)
    course_id = validate_uuid(course_id)

    created_record = await sync_to_async(Wishlist.objects.create)(
        user_id=user_id,
        course_id=course_id
    )

    from courses.services.cache_service import invalidate_courses_by_user_id_cache
    await invalidate_courses_by_user_id_cache(user_id)

    return created_record
