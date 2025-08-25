import logging

from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.utils.translation import gettext

from smartStudy_backend import settings
from ..models import UserSettings, UserProfile, CustomUser

logger = logging.getLogger(__name__)

PROFILE_CACHE_TIMEOUT = 60 * 60
SETTINGS_CACHE_TIMEOUT = 24 * 60 * 60
USER_STATUS_CACHE_TIMEOUT = 30 * 60
USER_EXISTENCE_CACHE_TIMEOUT = 10 * 60
GOOGLE_TOKEN_CACHE_TIMEOUT = 15 * 60
RATE_LIMIT_TIMEOUT = 5 * 60

async def get_allowed_roles():
    """Caching the list of allowed roles"""
    cache_key = "allowed_roles"
    roles = await sync_to_async(cache.get)(cache_key)

    if not roles:
        roles = settings.ALLOWED_ROLES
        await sync_to_async(cache.set)(cache_key, roles, timeout=12 * 60 * 60)

    return roles

def get_user_existence_cache_key(email):
    return f"user_exists_{hash(email)}"

def get_profile_cache_key(user_id):
    return f"user_profile_{user_id}"

def get_settings_cache_key(user_id):
    return f"user_settings_{user_id}"

def get_user_status_cache_key(user_id):
    return f"user_status_{user_id}"

async def get_user_existence_cache(email):
    """Caching user existence checks"""
    if not email:
        return {"exists": False}

    cache_key = get_user_existence_cache_key(email)
    user_data = await sync_to_async(cache.get)(cache_key)

    if user_data is None:
        try:
            user = await sync_to_async(CustomUser.objects.get)(email=email)
            user_data = {
                "exists": True,
                "is_active": user.is_active,
                "is_verified": user.is_verified_email,
                "id": user.id
            }
        except CustomUser.DoesNotExist:
            user_data = {"exists": False}

        await sync_to_async(cache.set)(cache_key, user_data, USER_EXISTENCE_CACHE_TIMEOUT)

    return user_data

async def get_cached_user_settings(user):
    """Caching user settings."""
    cache_key = get_settings_cache_key(user.id)
    cached_settings = await sync_to_async(cache.get)(cache_key)

    if cached_settings:
        return cached_settings

    try:
        user_settings, _ = await sync_to_async(UserSettings.objects.get_or_create)(user=user)
        settings_data = {
            "email_notifications": user_settings.email_notifications,
            "push_notifications": user_settings.push_notifications,
            "deadline_reminders": user_settings.deadline_reminders,
            "show_profile_to_others": user_settings.show_profile_to_others,
            "show_achievements": user_settings.show_achievements,
        }
        await sync_to_async(cache.set)(cache_key, settings_data, SETTINGS_CACHE_TIMEOUT)
        return settings_data
    except Exception as e:
        logger.error(f"{gettext("Error receiving user settings")} {user.id}: {str(e)}")
        return {}

async def get_cached_user_status(user):
    """Caching user status"""
    cache_key = get_user_status_cache_key(user.id)
    cached_status = await sync_to_async(cache.get)(cache_key)

    if cached_status is not None:
        return cached_status

    status_data = {
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "is_verified_email": user.is_verified_email,
    }
    await sync_to_async(cache.set)(cache_key, status_data, USER_STATUS_CACHE_TIMEOUT)
    return status_data

async def get_cached_profile(user):
    """Caching user profiles."""
    cache_key = get_profile_cache_key(user.id)
    cached_data = await sync_to_async(cache.get)(cache_key)

    if cached_data:
        return cached_data

    try:
        user_profile, _ = await sync_to_async(UserProfile.objects.get_or_create)(user=user)

        settings_data = await get_cached_user_settings(user)
        status_data = await get_cached_user_status(user)

        profile_data = {
            "user": {
                "id": str(user.id),
                "name": user.name,
                "surname": user.surname,
                "email": user.email,
                "phone_number": user.phone_number if user.phone_number else None,
                "role": user.role,
                **status_data
            },
            "settings": settings_data,
            "profile": {
                "bio": user_profile.bio if user_profile.bio else None,
                "profile_picture": user_profile.profile_picture if user_profile.profile_picture else None,
                "location": user_profile.location if user_profile.location else None,
                "organization": user_profile.organization if user_profile.organization else None,
                "specialization": user_profile.specialization if user_profile.specialization else None,
                "education_level": user_profile.education_level if user_profile.education_level else None,
            }
        }

        await sync_to_async(cache.set)(cache_key, profile_data, PROFILE_CACHE_TIMEOUT)
        return profile_data

    except Exception as e:
        logger.error(f"{gettext("Error receiving user profile")} {user.id}: {str(e)}")
        return {
            "user": {
                "id": str(user.id),
                "name": user.name,
                "surname": user.surname,
                "email": user.email,
                "role": user.role,
            },
            "settings": {},
            "profile": {}
        }

async def invalidate_user_existence_cache(email):
    """Invalidating the user existence cache"""
    cache_key = get_user_existence_cache_key(email)
    result = await sync_to_async(cache.delete)(cache_key)
    logger.info(f"{gettext("Invalidating the user existence cache for email:")} {email} - {gettext('successfully') if result else gettext('key not found')}")
    return result

async def invalidate_user_cache(user_id):
    """Delete all cached user data."""
    cache_keys = [
        get_profile_cache_key(user_id),
        get_settings_cache_key(user_id),
        get_user_status_cache_key(user_id)
    ]
    delete_count = await sync_to_async(cache.delete_many)(cache_keys)
    logger.info(f"{gettext("Deleted")} {delete_count} {gettext("cached user records")} {user_id}")
    return delete_count


async def invalidate_all_user_caches(user_id, email=None):
    """Complete invalidation of all user caches"""
    count = await invalidate_user_cache(user_id)
    if email:
        await invalidate_user_existence_cache(email)
        count += 1

    logger.info(f"{gettext("Complete invalidation of caches for the user")} {user_id}: {count} {gettext("records")}")
    return count

async def invalidate_user_settings_cache(user_id):
    """Delete only the settings cache"""
    cache_key = get_settings_cache_key(user_id)
    await sync_to_async(cache.delete)(cache_key)
    await sync_to_async(cache.delete)(get_profile_cache_key(user_id))
    logger.info(f"{gettext("Disabled cache settings and user profile")} {user_id}")

async def invalidate_user_profile_cache(user_id):
    """Delete only the profile cache"""
    cache_key = get_profile_cache_key(user_id)
    result = await sync_to_async(cache.delete)(cache_key)
    logger.info(f"{gettext("Disabled profile cache for user")} {user_id} - {gettext('successfully') if result else gettext('key not found')}")
    return result

async def warm_user_cache(user, warm_existence=True):
    """Preloading the cache for the user"""
    try:
        await get_cached_profile(user)

        if warm_existence:
            await get_user_existence_cache(user.email)

        logger.info(f"{gettext("Cache warmed up for the user")} {user.id}")
    except Exception as e:
        logger.error(f"{gettext("Error while warming up the user cache")} {user.id}: {str(e)}")
