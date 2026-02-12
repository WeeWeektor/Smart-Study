from asgiref.sync import sync_to_async
from django.db.models import Case, When

from courses.models import Course
from courses.utils import generate_course_json_with_details_and_owner
from ml_model.recommender import courses_recommender


async def get_course_recommendations(course_id, status_param, limit_param):
    recommended_ids = await sync_to_async(courses_recommender.get_recommendations)(
        course_id=course_id,
        status=status_param,
        limit=int(limit_param)
    )

    courses = []
    if recommended_ids:
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(recommended_ids)])
        courses_qs = Course.objects.filter(id__in=recommended_ids).order_by(preserved_order)
        courses = [course async for course in courses_qs]

    courses_data = await generate_course_json_with_details_and_owner(courses)

    return courses_data
