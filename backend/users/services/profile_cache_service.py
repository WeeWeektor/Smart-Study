from django.core.cache import cache
from ..models import UserSettings, UserProfile

CACHE_TIMEOUT = 60 * 0.5

def get_cache_key(user_id):
    return f"user_profile_{user_id}"

def get_cached_profile(user):
    cache_key = get_cache_key(user.id)
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    user_settings, _ = UserSettings.objects.get_or_create(user=user)
    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    profile_data = {
        "user": {
            "id": str(user.id),
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "phone_number": user.phone_number if user.phone_number else None,
            "role": user.role,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_verified_email": user.is_verified_email,
        },
        "settings": {
            "email_notifications": user_settings.email_notifications,
            "push_notifications": user_settings.push_notifications,
            "deadline_reminders": user_settings.deadline_reminders,
            "show_profile_to_others": user_settings.show_profile_to_others,
            "show_achievements": user_settings.show_achievements,
        },
        "profile": {
            "bio": user_profile.bio if user_profile.bio else None,
            "profile_picture": user_profile.profile_picture if user_profile.profile_picture else None,
            "location": user_profile.location if user_profile.location else None,
            "organization": user_profile.organization if user_profile.organization else None,
            "specialization": user_profile.specialization if user_profile.specialization else None,
            "education_level": user_profile.education_level if user_profile.education_level else None,
        }
    }
    cache.set(cache_key, profile_data, CACHE_TIMEOUT)
    return profile_data

def invalidate_cache(user_id):
    cache_key = get_cache_key(user_id)
    cache.delete(cache_key)
