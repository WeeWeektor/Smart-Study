from django.utils.translation import gettext

from common.utils import validate_uuid, error_response
from courses.models import Course
from courses.utils import generate_course_json_with_details_and_owner


async def get_courses_by_user(user_id):
    # TODO Тут має бути логіка отримання всіх курсів користувача (з вішлиста, тих що він проходить і ті які він вже пройшов)

    try:
        user_id = validate_uuid(user_id)

        wishlist_courses_queryset = (Course.objects
                                     .filter(wishlisted_by__user_id=user_id)
                                     .select_related('owner', 'details'))

        wishlist_courses = [course async for course in wishlist_courses_queryset]
        in_wishlist = await generate_course_json_with_details_and_owner(wishlist_courses)

        is_enrolled = []
        is_completed = []

        return in_wishlist, is_enrolled, is_completed
    except Exception as e:
        return error_response(gettext("Error retrieving courses") + str(e), status=500)
