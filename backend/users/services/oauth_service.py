from django.contrib.auth import login, get_user_model
from django.http import JsonResponse
from django.core.cache import cache
from django.utils.crypto import get_random_string

from smartStudy_backend import settings
from users.models import UserSettings
from users.services.profile_cache_service import warm_user_cache, invalidate_user_existence_cache, get_allowed_roles

from google.oauth2 import id_token
from google.auth.transport import requests


def verify_facebook_token(token):
    """Verify the Facebook OAuth token and return user info."""
    app_id = settings.SOCIAL_AUTH_FACEBOOK_KEY
    app_secret = settings.SOCIAL_AUTH_FACEBOOK_SECRET

    debug_url = f"https://graph.facebook.com/debug_token"
    debug_params = {
        "input_token": token,
        "access_token": f"{app_id}|{app_secret}"
    }

    debug_response = requests.get(debug_url, params=debug_params)
    debug_data = debug_response.json()

    if not debug_data.get("data", {}).get("is_valid"):
        raise ValueError("Invalid Facebook token")

    user_url = "https://graph.facebook.com/me"
    user_params = {
        "fields": "id,name,email,first_name,last_name",
        "access_token": token
    }

    user_response = requests.get(user_url, params=user_params)
    user_data = user_response.json()

    if "error" == user_data:
        raise ValueError("Помилка Facebook API: " + user_data["error"]["message"])

    return {
        "email": user_data.get("email"),
        "name": user_data.get("first_name", ""),
        "given_name": user_data.get("first_name", ""),
        "family_name": user_data.get("last_name", ""),
        "sub": user_data.get("id"),
    }


def handle_oauth_login(request, token, provider, name=None, surname=None, role=None, phone_number=None,
                       email_notifications=True, push_notifications=True):
    try:
        cache_key = f"{provider}_token_{hash(token)}"
        idinfo = cache.get(cache_key)

        if not idinfo:
            if provider == "google":
                idinfo = id_token.verify_oauth2_token(
                    token, requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
                )
            elif provider == "facebook":
                idinfo = verify_facebook_token(token)
            else:
                raise ValueError("Невідомий провайдер OAuth")

            cache.set(cache_key, idinfo, timeout=15*60)

        email = idinfo['email']
        oauth_name = idinfo.get('given_name') or idinfo.get('name') or name or ''
        oauth_surname = idinfo.get('family_name') or surname or ''

        User = get_user_model()
        user = User.objects.filter(email=email).first()

        if user:
            if not user.is_verified_email:
                user.is_verified_email = True
            if not user.is_active:
                user.is_active = True
            user.save()

            invalidate_user_existence_cache(email)
            warm_user_cache(user)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return JsonResponse({
                'user': {
                    'email': user.email,
                    'name': user.name,
                    'surname': user.surname,
                    'role': user.role,
                },
                'message': f'Успішна авторизація через {provider} (сесія)'
            }, status=200)

        if not role or not oauth_surname:
            return JsonResponse({'error': 'Необхідно вказати role та surname'}, status=400)

        if role not in get_allowed_roles():
            return JsonResponse({
                "error": f"Невірна роль. Допустимі значення: {', '.join(get_allowed_roles())}"
            }, status=400)

        user = User.objects.create_user(
            name=oauth_name,
            surname=oauth_surname,
            role=role,
            phone_number=phone_number,
            email=email,
            password=get_random_string(12),
            is_verified_email=True,
            is_active=True,
        )

        invalidate_user_existence_cache(email)

        UserSettings.objects.create(
            user=user,
            email_notifications=email_notifications,
            push_notifications=push_notifications,
        )

        warm_user_cache(user)

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return JsonResponse({
            'user': {
                'email': user.email,
                'name': user.name,
                'surname': user.surname,
                'role': user.role,
            },
            'message': f'Успішна реєстрація та авторизація через {provider} (сесія)'
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
