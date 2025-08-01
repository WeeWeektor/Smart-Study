import logging
from django.core.cache import cache

from smartStudy_backend import settings
from ..models import UserSettings, UserProfile, CustomUser

logger = logging.getLogger(__name__)

PROFILE_CACHE_TIMEOUT = 60 * 60
SETTINGS_CACHE_TIMEOUT = 24 * 60 * 60
USER_STATUS_CACHE_TIMEOUT = 30 * 60
USER_EXISTENCE_CACHE_TIMEOUT = 10 * 60
GOOGLE_TOKEN_CACHE_TIMEOUT = 15 * 60
RATE_LIMIT_TIMEOUT = 5 * 60

def get_allowed_roles():
    """Кешування списку дозволених ролей"""
    cache_key = "allowed_roles"
    roles = cache.get(cache_key)

    if not roles:
        roles = settings.ALLOWED_ROLES
        cache.set(cache_key, roles, timeout=12 * 60 * 60)

    return roles

def get_user_existence_cache_key(email):
    return f"user_exists_{hash(email)}"

def get_profile_cache_key(user_id):
    return f"user_profile_{user_id}"

def get_settings_cache_key(user_id):
    return f"user_settings_{user_id}"

def get_user_status_cache_key(user_id):
    return f"user_status_{user_id}"

def get_user_existence_cache(email):
    """Кешування перевірки існування користувача"""
    if not email:
        return {"exists": False}

    cache_key = get_user_existence_cache_key(email)
    user_data = cache.get(cache_key)

    if user_data is None:
        try:
            user = CustomUser.objects.get(email=email)
            user_data = {
                "exists": True,
                "is_active": user.is_active,
                "is_verified": user.is_verified_email,
                "id": user.id
            }
        except CustomUser.DoesNotExist:
            user_data = {"exists": False}

        cache.set(cache_key, user_data, USER_EXISTENCE_CACHE_TIMEOUT)

    return user_data

def get_cached_user_settings(user):
    """Кешування налаштувань користувача."""
    cache_key = get_settings_cache_key(user.id)
    cached_settings = cache.get(cache_key)

    if cached_settings:
        return cached_settings

    try:
        user_settings, _ = UserSettings.objects.get_or_create(user=user)
        settings_data = {
            "email_notifications": user_settings.email_notifications,
            "push_notifications": user_settings.push_notifications,
            "deadline_reminders": user_settings.deadline_reminders,
            "show_profile_to_others": user_settings.show_profile_to_others,
            "show_achievements": user_settings.show_achievements,
        }
        cache.set(cache_key, settings_data, SETTINGS_CACHE_TIMEOUT)
        return settings_data
    except Exception as e:
        logger.error(f"Помилка при отриманні налаштувань користувача {user.id}: {str(e)}")
        return {}

def get_cached_user_status(user):
    """Кешування статусу користувача"""
    cache_key = get_user_status_cache_key(user.id)
    cached_status = cache.get(cache_key)

    if cached_status is not None:
        return cached_status

    status_data = {
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "is_verified_email": user.is_verified_email,
    }
    cache.set(cache_key, status_data, USER_STATUS_CACHE_TIMEOUT)
    return status_data

def get_cached_profile(user):
    """Кешування профілю користувача."""
    cache_key = get_profile_cache_key(user.id)
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    try:
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        settings_data = get_cached_user_settings(user)
        status_data = get_cached_user_status(user)

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

        cache.set(cache_key, profile_data, PROFILE_CACHE_TIMEOUT)
        return profile_data

    except Exception as e:
        logger.error(f"Помилка при отриманні профілю користувача {user.id}: {str(e)}")
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

def invalidate_user_existence_cache(email):
    """Інвалідація кешу існування користувача"""
    cache_key = get_user_existence_cache_key(email)
    result = cache.delete(cache_key)
    logger.info(f"Інвалідація кешу існування користувача для email: {email} - {'успішно' if result else 'ключ не знайдено'}")
    return result

def invalidate_user_cache(user_id):
    """Видалення всіх кешованих даних користувача."""
    cache_keys = [
        get_profile_cache_key(user_id),
        get_settings_cache_key(user_id),
        get_user_status_cache_key(user_id)
    ]
    delete_count = cache.delete_many(cache_keys)
    logger.info(f"Видалено {delete_count} кешованих записів для користувача {user_id}")
    return delete_count


def invalidate_all_user_caches(user_id, email=None):
    """Повна інвалідація всіх кешів користувача"""
    count = invalidate_user_cache(user_id)
    if email:
        invalidate_user_existence_cache(email)
        count += 1

    logger.info(f"Повна інвалідація кешів для користувача {user_id}: {count} записів")
    return count

def invalidate_user_settings_cache(user_id):
    """Видалення тільки кешу налаштувань"""
    cache_key = get_settings_cache_key(user_id)
    cache.delete(cache_key)
    cache.delete(get_profile_cache_key(user_id))
    logger.info(f"Інвалідовано кеш налаштувань та профілю для користувача {user_id}")

def invalidate_user_profile_cache(user_id):
    """Видалення тільки кешу профілю"""
    cache_key = get_profile_cache_key(user_id)
    result = cache.delete(cache_key)
    logger.info(f"Інвалідовано кеш профілю для користувача {user_id} - {'успішно' if result else 'ключ не знайдено'}")
    return result

def warm_user_cache(user, warm_existence=True):
    """Попереднє завантаження кешу для користувача"""
    try:
        get_cached_profile(user)

        if warm_existence:
            get_user_existence_cache(user.email)

        logger.info(f"Кеш прогрітий для користувача {user.id}")
    except Exception as e:
        logger.error(f"Помилка при прогріві кешу для користувача {user.id}: {str(e)}")
