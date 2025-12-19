from asgiref.sync import sync_to_async

from common.utils import validate_uuid
from courses.models import CourseReview
from courses.services import validate_course_review_data


async def create_review_of_course(data, user):
    user_id = validate_uuid(user.id)
    course_id = data.get("course_id")
    validate_course_review_data(data)

    review, _ = await sync_to_async(CourseReview.objects.update_or_create)(
        course_id=course_id,
        user_id=user_id,
        defaults={
            "rating": data.get("rating"),
            "comment": data.get("comment", "").strip(),
        }
    )

    from courses.services.cache_service import invalidate_course_review_cache
    await invalidate_course_review_cache(course_id)

    return review
