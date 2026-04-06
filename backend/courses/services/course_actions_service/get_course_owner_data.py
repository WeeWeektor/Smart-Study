from asgiref.sync import sync_to_async

from users.models import CustomUser


async def get_course_owner_data(owner_id):
    owner = await sync_to_async(CustomUser.objects.select_related("profile", "settings").get)(pk=owner_id)

    is_public = owner.settings.show_profile_to_others

    owner_data = {
        "owner": {
            "id": str(owner_id),
            "name": owner.name,
            "surname": owner.surname,
        },
        "profile": {
            "profile_picture": owner.profile.profile_picture or None,
        },
        "settings": {
            "show_profile_to_others": is_public,
            "show_achievements": owner.settings.show_achievements,
        }
    }

    if is_public:
        owner_data["owner"].update({
            "email": owner.email,
            "phone_number": owner.phone_number or None,
        })

        owner_data["profile"].update({
            "bio": owner.profile.bio or None,
            "location": owner.profile.location or None,
            "organization": owner.profile.organization or None,
            "specialization": owner.profile.specialization or None,
            "education_level": owner.profile.education_level or None,
        })

    return owner_data
