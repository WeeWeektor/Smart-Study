import json
from typing import Optional

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import redirect
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.http import JsonResponse

from smartStudy_backend import settings
from .models import CustomUser, UserSettings, UserProfile
from .user_utils import send_verification_email, error_response, success_response, send_password_reset_email
from .utils.validators import email_validator, phone_validator
from .utils.request_parsing import parse_request_data
from .services.profile_picture_service import handle_profile_picture
from .services.profile_cache_service import get_cached_profile, invalidate_cache
from .services.profile_update_service import update_user_data, update_user_settings, update_user_profile

from rest_framework.views import APIView
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model


@method_decorator(ensure_csrf_cookie, name="dispatch")
class RegisterView(View):
    @staticmethod
    def post(request):
        try:
            data = json.loads(request.body)

            required_fields = ['name', 'surname', 'role', 'email', 'password']
            for field in required_fields:
                if field not in data:
                    return error_response(f"Відсутнє обов'язкове поле: {field}")

            try:
                email_validator(data['email'])
            except ValidationError as e:
                return error_response(str(e))

            try:
                validate_password(data['password'])
            except ValidationError as e:
                return error_response(', '.join(e.messages))

            try:
                if data['phone_number'] is not None:
                    phone_validator(data['phone_number'])
            except ValidationError as e:
                return error_response(str(e))

            if data['role'] not in settings.ALLOWED_ROLES:
                return error_response(f'Невірна роль. Допустимі значення: {", ".join(settings.ALLOWED_ROLES)}')

            if not data['name'].strip() or not data['surname'].strip():
                return error_response("Ім'я та прізвище не можуть бути порожніми.")

            user = CustomUser.objects.create_user(
                name=data['name'],
                surname=data['surname'],
                phone_number=data['phone_number'],
                role=data['role'],
                email=data['email'],
                password=data['password'],
            )
            user.is_active = False
            user.save()

            UserSettings.objects.create(
                user=user,
                email_notifications=data.get('email_notifications', True),
                push_notifications=data.get('push_notifications', True)
            )

            send_verification_email(user)
            return success_response({"message": "Будь ласка, підтвердіть email."})
        except IntegrityError:
            return error_response("Email вже зайнятий.")
        except json.JSONDecodeError:
            return error_response("Невірний формат JSON.")
        except Exception as e:
            return error_response(f"Помилка при реєстрації: {str(e)}", 500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class VerifyEmailView(View):
    @staticmethod
    def get(request):
        token = request.GET.get('token')

        if not token:
            return error_response('Невірний токен. Параметр \'token\' відсутній.')

        signer = TimestampSigner()
        try:
            email = signer.unsign(token, max_age=60 * 60 * 24)
            try:
                user = CustomUser.objects.get(email=email)
                if user.is_verified_email:
                    return success_response({"message": "Email вже підтверджено."})

                user.is_verified_email = True
                user.is_active = True
                user.save()
                login(request, user)
                return redirect(f"{settings.FRONTEND_URL}/")
            except CustomUser.DoesNotExist:
                return error_response("Користувача з таким email не знайдено.")
        except SignatureExpired:
            return error_response("Термін дії посилання для підтвердження закінчився.")
        except BadSignature:
            return error_response("Невірний токен для підтвердження.")


@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginView(View):
    @staticmethod
    def post(request):
        try:
            data = json.loads(request.body)

            if 'email' not in data or 'password' not in data:
                return error_response('Відсутні обов\'язкові поля: email або password.')

            email = data['email']
            password = data['password']

            try:
                email_validator(email)
            except ValidationError as e:
                return error_response(str(e))

            user: Optional[CustomUser] = authenticate(request, username=email, password=password)

            if user is None:
                return error_response('Неправильний email або пароль.', 400)

            if not user.is_active:
                return error_response('Обліковий запис неактивний.', 400)

            if not user.is_verified_email:
                return error_response('Email не підтверджено. Перевірте вашу пошту.', 400)

            login(request, user)
            return success_response({
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                    "surname": user.surname,
                    "email": user.email,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "phone_number": user.phone_number,
                    "role": user.role,
                    "is_verified_email": user.is_verified_email,
                },
                "redirect": "/admin/" if user.is_staff or user.is_superuser else "/",
            })
        except json.JSONDecodeError:
            return error_response("Невірний формат JSON.", 400)
        except Exception as e:
            return error_response(f"Помилка при вході: {str(e)}", 500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class GoogleAuthView(APIView):
    permission_classes = []

    @staticmethod
    def post(request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        token = data.get('credential')
        role = data.get('role')
        surname = data.get('surname')
        name = data.get('name')
        phone_number = data.get('phone_number')
        if not token:
            return JsonResponse({'error': 'No credential provided'}, status=400)
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY)
            email = idinfo['email']
            google_name = idinfo.get('given_name') or idinfo.get('name') or name or ''
            google_surname = idinfo.get('family_name') or surname or ''
            User = get_user_model()
            user = User.objects.filter(email=email).first()
            if user:
                if not user.is_verified_email:
                    user.is_verified_email = True
                if not user.is_active:
                    user.is_active = True
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return JsonResponse({
                    'user': {
                        'email': user.email,
                        'name': user.name,
                        'surname': user.surname,
                        'role': user.role,
                    },
                    'message': 'Успішна авторизація через Google (сесія)'
                }, status=200)
            if not role or not google_surname:
                return JsonResponse({'error': 'Необхідно вказати role та surname'}, status=400)
            user = User.objects.create_user(
                name=google_name,
                surname=google_surname,
                role=role,
                phone_number=phone_number,
                email=email,
                password=User.objects.make_random_password(),
                is_verified_email=True,
                is_active=True,
            )
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return JsonResponse({
                'user': {
                    'email': user.email,
                    'name': user.name,
                    'surname': user.surname,
                    'role': user.role,
                },
                'message': 'Успішна реєстрація та авторизація через Google (сесія)'
            }, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ForgotPasswordView(View):
    @staticmethod
    def post(request):
        try:
            data = json.loads(request.body)
            email = data['email']

            if not email:
                return error_response("Відсутня електронна пошта.")

            try:
                email_validator(email)
            except ValidationError as e:
                return error_response(str(e))

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return error_response("Користувача з таким email не знайдено.", 404)

            if not user.is_active:
                return error_response('Обліковий запис неактивний.', 400)

            if not user.is_verified_email:
                return error_response("Email не підтверджено. Перевірте вашу пошту.", 400)

            send_password_reset_email(user)
            return success_response({"message": "Будь ласка, перевірте вашу пошту для скидання паролю."})
        except KeyError:
            return error_response("Відсутнє поле: email")
        except json.JSONDecodeError:
            return error_response("Невірний формат JSON.", 400)
        except Exception as e:
            return error_response(f"Помилка при обробці запиту: {str(e)}", 500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ResetPasswordView(View):
    @staticmethod
    def get(request):
        token = request.GET.get('token')

        if not token:
            return error_response('Відсутній токен для скидання паролю.', 400)

        signer = TimestampSigner()
        try:
            email = signer.unsign(token, max_age=60 * 60 * 24)
            try:
                CustomUser.objects.get(email=email)
                return redirect(f"{settings.FRONTEND_URL}/reset-password?token={token}")
            except CustomUser.DoesNotExist:
                return error_response("Користувача з таким email не знайдено.", 404)
        except SignatureExpired:
            return error_response("Термін дії токена для скидання паролю закінчився.", 400)
        except BadSignature:
            return error_response("Невірний токен для скидання паролю.", 400)

    @staticmethod
    def post(request):
        try:
            data = json.loads(request.body)

            if 'token' not in data or 'password' not in data:
                return error_response('Відсутні обов\'язкові поля: token або password.')

            token = data['token']
            password = data['password']

            try:
                validate_password(password)
            except ValidationError as e:
                return error_response(', '.join(e.messages))

            signer = TimestampSigner()
            try:
                email = signer.unsign(token, max_age=60 * 60 * 24)
                try:
                    user = CustomUser.objects.get(email=email)
                    user.set_password(password)
                    user.save()

                    return success_response({"message": "Пароль успішно змінено"})
                except CustomUser.DoesNotExist:
                    return error_response("Користувача з таким email не знайдено.", 404)
            except SignatureExpired:
                return error_response("Термін дії токена для скидання паролю закінчився.", 400)
            except BadSignature:
                return error_response("Невірний токен для скидання паролю.", 400)
        except json.JSONDecodeError:
            return error_response("Невірний формат JSON.", 400)
        except Exception as e:
            return error_response(f"Помилка при скиданні паролю: {str(e)}", 500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class LogoutView(View):
    @staticmethod
    def post(request):
        logout(request)
        return success_response({"message": "Успішний вихід з системи."})


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ChangePasswordView(View):
    @staticmethod
    def patch(request):
        if not request.user.is_authenticated:
            return error_response("Користувач не авторизований.", 401)

        try:
            data = json.loads(request.body)

            if 'current_password' not in data or 'new_password' not in data or 'confirm_password' not in data:
                return error_response(
                    'Відсутні обов\'язкові поля: current_password, new_password або confirm_password.')

            current_password = data['current_password']
            new_password = data['new_password']
            confirm_password = data['confirm_password']

            if new_password != confirm_password:
                return error_response("Новий пароль і підтвердження паролю не збігаються.", 400)

            try:
                validate_password(new_password)
            except ValidationError as e:
                return error_response(', '.join(e.messages))

            user = request.user
            if not user.check_password(current_password):
                return error_response("Невірний поточний пароль.", 400)

            user.set_password(new_password)
            user.save()
            login(request, user)

            return success_response({"message": "Пароль успішно змінено."})
        except json.JSONDecodeError:
            return error_response("Невірний формат JSON.", 400)
        except Exception as e:
            return error_response(f"Помилка при зміні паролю: {str(e)}", 500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ProfileView(View):
    CACHE_TIMEOUT = 60 * 0.5

    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            return error_response("Користувач не авторизований.", 401)

        try:
            profile_data = get_cached_profile(request.user)
            return success_response(profile_data)
        except Exception as e:
            return error_response(f"Помилка при отриманні профілю: {str(e)}", 500)

    @staticmethod
    def post(request):
        """Окремий ендпоінт для завантаження аватарки"""
        if not request.user.is_authenticated:
            return error_response("Користувач не авторизований.", 401)

        try:
            if 'profile_picture' not in request.FILES:
                return error_response("Файл не знайдено.", 400)

            profile_picture = request.FILES['profile_picture']
            user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

            handle_profile_picture(user_profile, profile_picture)
            invalidate_cache(request.user.id)

            return success_response({
                "url": user_profile.profile_picture,
                "message": "Аватарку успішно завантажено."
            })

        except ValidationError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f"Помилка при завантаженні аватарки: {str(e)}", 500)

    @staticmethod
    def patch(request):
        if not request.user.is_authenticated:
            return error_response("Користувач не авторизований.", 401)

        try:
            data, is_multipart = parse_request_data(request)
            user = request.user

            update_user_data(user, data.get('user', {}))
            update_user_settings(user, data.get('settings', {}), is_multipart)
            update_user_profile(user, data.get('profile', {}))

            if 'profile_picture' in request.FILES:
                user_profile = UserProfile.objects.get(user=user)
                handle_profile_picture(user_profile, request.FILES['profile_picture'])

            invalidate_cache(user.id)
            updated_profile_data = get_cached_profile(user)

            return success_response({
                "message": "Профіль успішно оновлено.",
                "profile_data": updated_profile_data
            })

        except json.JSONDecodeError:
            return error_response("Невірний формат JSON.", 400)
        except ValidationError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f"Помилка при оновленні профілю: {str(e)}", 500)

    @staticmethod
    def delete(request):
        if not request.user.is_authenticated:
            return error_response("Користувач не авторизований.", 401)

        try:
            user = request.user
            user_id = user.id

            logout(request)
            user.delete()
            invalidate_cache(user_id)

            return success_response({"message": "Обліковий запис успішно видалено."})
        except Exception as e:
            return error_response(f"Помилка при видаленні облікового запису: {str(e)}", 500)
