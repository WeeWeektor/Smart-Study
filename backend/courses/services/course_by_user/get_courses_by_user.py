import uuid

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

        is_enrolled = [
            generate_mock_course("Data Science з нуля1", category="data_science", level="intermediate"),
            generate_mock_course("Data Science з нуля2", category="data_science", level="intermediate"),
            generate_mock_course("Data Science з нуля3", category="data_science", level="intermediate"),
            generate_mock_course("Data Science з нуля4", category="data_science", level="intermediate"),
        ]
        is_completed = [
            generate_mock_course("Data Science з нуля1", category="data_science", level="intermediate"),
            generate_mock_course("Data Science з нуля2", category="data_science", level="intermediate"),
            generate_mock_course("Data Science з нуля3", category="data_science", level="intermediate"),
            generate_mock_course("Data Science з нуля4", category="data_science", level="intermediate"),
        ]

        return in_wishlist, is_enrolled, is_completed
    except Exception as e:
        return error_response(gettext("Error retrieving courses") + str(e), status=500)


def generate_mock_course(title, category="programming", level="beginner"):
    course_id = str(uuid.uuid4())
    owner_id = str(uuid.uuid4())

    return {
        "course": {
            "id": course_id,
            "title": title,
            "description": f"Це опис для курсу '{title}'. Тут ви дізнаєтесь багато цікавого про {category}.",
            "category": category,
            "owner": {
                "id": owner_id,
                "name": "Іван",
                "surname": "Петренко",
                "email": "ivan@example.com",
                "profile_picture": None
            },
            "cover_image": "https://placehold.co/600x400/2563eb/ffffff?text=Course",
            "is_published": True,
            "created_at": "2023-10-10T10:00:00Z",
            "published_at": "2023-10-12T10:00:00Z",
            "updated_at": None,
            "version": 1,
            "structure_ids": str(uuid.uuid4()),
            "structure": {"_id": str(uuid.uuid4())},
            "details": {
                "total_modules": 5,
                "total_lessons": 12,
                "total_tests": 3,
                "time_to_complete": "PT15H",
                "course_language": "ua",
                "rating": 4.8,
                "level": level,
                "number_completed": 120,
                "number_of_active": 45,
                "feedback_count": 15,
                "feedback_summary": {"5": 10, "4": 5}
            }
        }
    }