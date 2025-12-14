from asgiref.sync import sync_to_async
from django.core.cache import caches

from common.services import register_cache_key
from common.utils import validate_uuid
from courses.models import Course
from users.models import CustomUser


async def _owner_course_data_cache_key(course_id) -> str:
    key = f"owner_course_data_id_{course_id}"

    await register_cache_key(key, "courses_get")
    return key


async def get_course_owner_data(course_id):
    uuid_obj = validate_uuid(course_id)
    instance_cache = caches["courses_get"]
    cache_key = await _owner_course_data_cache_key(uuid_obj)

    ownerDataCourseId = await sync_to_async(instance_cache.get)(cache_key, version=1, default=None)
    if ownerDataCourseId:
        return ownerDataCourseId

    owner_id = await sync_to_async(Course.objects.only("owner").get)(pk=uuid_obj)

    ownerData = await _get_owner_data(owner_id.owner_id)

    if ownerData["settings"]["show_profile_to_others"] is False:
        ownerData = {
            "owner": {
                "id": str(ownerData["owner"]["id"]),
                "name": ownerData["owner"]["name"],
                "surname": ownerData["owner"]["surname"],
            },
            "profile": {
                "profile_picture": ownerData["profile"]["profile_picture"] if ownerData["profile"]["profile_picture"] else None,
            },
            "settings": {
                "show_profile_to_others": ownerData["settings"]["show_profile_to_others"],
                "show_achievements": ownerData["settings"]["show_achievements"],
            }
        }

    await sync_to_async(instance_cache.set)(cache_key, ownerData, 60 * 60, version=1)

    return ownerData


async def _get_owner_data(ownerId) -> dict:
    ownerData = await sync_to_async(CustomUser.objects.select_related("profile", "settings").get)(pk=ownerId)

    ownerDataResponse = {
        "owner": {
            "id": str(ownerId),
            "name": ownerData.name,
            "surname": ownerData.surname,
            "email": ownerData.email,
            "phone_number": ownerData.phone_number if ownerData.phone_number else None,
        },
        "settings": {
            "show_profile_to_others": ownerData.settings.show_profile_to_others,
            "show_achievements": ownerData.settings.show_achievements,
        },
        "profile": {
            "bio": ownerData.profile.bio if ownerData.profile.bio else None,
            "profile_picture": ownerData.profile.profile_picture if ownerData.profile.profile_picture else None,
            "location": ownerData.profile.location if ownerData.profile.location else None,
            "organization": ownerData.profile.organization if ownerData.profile.organization else None,
            "specialization": ownerData.profile.specialization if ownerData.profile.specialization else None,
            "education_level": ownerData.profile.education_level if ownerData.profile.education_level else None,
        }
    }

    return ownerDataResponse
