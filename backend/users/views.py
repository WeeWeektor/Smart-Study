import asyncio
import json
from typing import Optional

from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.signing import BadSignature, SignatureExpired
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView, LocalizedAPIView
from common.decorators import login_required_async
from common.services import delete_picture, handle_picture
from common.utils import error_response, success_response, signer
from smartStudy_backend import settings
from .models import CustomUser, UserSettings, UserProfile
from .services.oauth_service import handle_oauth_login
from .services.profile_cache_service import (
    get_cached_profile,
    invalidate_user_cache,
    warm_user_cache,
    get_allowed_roles,
    get_user_existence_cache,
    invalidate_user_existence_cache, invalidate_all_user_caches
)
from .services.profile_update_service import update_user_data, update_user_settings, update_user_profile
from .user_utils import send_verification_email, send_password_reset_email
from common.utils.request_parsing import parse_request_data
from .utils.validators import cached_email_validator, phone_validator


@method_decorator(ensure_csrf_cookie, name="dispatch")
class RegisterView(LocalizedView):
    @staticmethod
    async def post(request):
        try:
            data = json.loads(request.body)

            required_fields = ['name', 'surname', 'role', 'email', 'password']
            for field in required_fields:
                if field not in data:
                    return error_response(f"{gettext("Required field missing:")} {field}")

            validation_tasks = [
                cached_email_validator(data['email']),
                sync_to_async(validate_password)(data['password']),
                get_allowed_roles(),
            ]

            if 'phone_number' in data and data['phone_number'] is not None:
                validation_tasks.insert(0, sync_to_async(phone_validator)(data['phone_number']))

            try:
                results = await asyncio.gather(*validation_tasks, return_exceptions=True)

                phone_validation_offset = 1 if 'phone_number' in data and data['phone_number'] is not None else 0
                validation_results = results[:-1]

                for i, result in enumerate(validation_results):
                    if isinstance(result, Exception):
                        if i == 0 and phone_validation_offset:
                            return error_response(f"Phone: {str(result)}")
                        elif (i == phone_validation_offset and 'email' in str(result).lower()) or (
                                i == 0 and not phone_validation_offset):
                            return error_response(f"Email: {str(result)}")
                        elif 'password' in str(result).lower():
                            return error_response(
                                f"Password: {', '.join(result.messages) if hasattr(result, 'messages') else str(result)}")
                        else:
                            return error_response(str(result))

                allowed_roles = results[-1]
                if isinstance(allowed_roles, Exception):
                    return error_response(str(allowed_roles))

            except Exception as e:
                return error_response(f"{gettext('Error during validation:')} {str(e)}")

            if data['role'] not in allowed_roles:
                return error_response(
                    f'{gettext("Incorrect role. Acceptable values:")} {", ".join(str(allowed_roles))}')

            if not data['name'].strip() or not data['surname'].strip():
                return error_response(gettext('First and last names cannot be left blank.'))

            async def create_user_with_settings():
                @sync_to_async
                def create_user_atomic():
                    with transaction.atomic():
                        user = CustomUser.objects.create_user(
                            name=data['name'].strip(),
                            surname=data['surname'].strip(),
                            phone_number=data.get('phone_number'),
                            role=data['role'],
                            email=data['email'],
                            password=data['password'],
                            is_active=False
                        )

                        UserSettings.objects.create(
                            user=user,
                            email_notifications=data.get('email_notifications', True),
                            push_notifications=data.get('push_notifications', True)
                        )

                        UserProfile.objects.create(user=user)

                        return user

                return await create_user_atomic()

            user = await create_user_with_settings()

            await asyncio.gather(
                invalidate_user_existence_cache(data['email']),
                send_verification_email(user)
            )

            return success_response({"message": gettext('Please confirm your email address.')})

        except IntegrityError:
            return error_response(gettext('Email already registered.'))
        except json.JSONDecodeError:
            return error_response(gettext('Invalid JSON format.'))
        except Exception as e:
            return error_response(f"{gettext('Error during registration:')} {str(e)}", 500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class VerifyEmailView(LocalizedView):
    @staticmethod
    async def get(request):
        token = request.GET.get('token')

        if not token:
            return error_response(gettext('Invalid token. The ‘token’ parameter is missing.'))

        try:
            email = signer.unsign(token, max_age=60 * 60 * 24)
            try:
                user = await sync_to_async(CustomUser.objects.get)(email=email)
                if user.is_verified_email:
                    return success_response({"message": gettext('Email already confirmed.')})

                user.is_verified_email = True
                user.is_active = True
                await sync_to_async(user.save)()

                await invalidate_user_existence_cache(email)

                await warm_user_cache(user)

                await sync_to_async(login)(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect(f"{settings.FRONTEND_URL}/verify-email?token={token}")
            except CustomUser.DoesNotExist:
                return error_response(gettext('No user with this email address was found.'))
        except SignatureExpired:
            return error_response(gettext('The confirmation link has expired.'))
        except BadSignature:
            return error_response(gettext("Invalid token for confirmation."))


@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginView(LocalizedView):
    @staticmethod
    async def post(request):
        try:
            data = json.loads(request.body)

            if 'email' not in data or 'password' not in data:
                return error_response(gettext('Required fields are missing: email or password.'))

            email = data['email']
            password = data['password']

            try:
                await cached_email_validator(email)
            except ValidationError as e:
                return error_response(str(e))

            user: Optional[CustomUser] = await sync_to_async(authenticate)(request, username=email, password=password)

            if user is None:
                return error_response(gettext('Incorrect email or password.'), 400)

            if not user.is_active:
                return error_response(gettext('Account is inactive.'), 400)

            if not user.is_verified_email:
                return error_response(gettext('Email not confirmed. Please check your email.'), 400)

            await sync_to_async(login)(request, user, backend='django.contrib.auth.backends.ModelBackend')

            await warm_user_cache(user)

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
                "redirect": "/profile/",
                # "redirect": "/admin/" if user.is_staff or user.is_superuser else "/",
            })
        except json.JSONDecodeError:
            return error_response(gettext('Invalid JSON format.'), 400)
        except Exception as e:
            return error_response(f"{gettext('Login error:')} {str(e)}", 500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class BaseAuthView(LocalizedAPIView):
    provider = None

    async def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body)
            token = data.get('credential')

            if not token:
                return JsonResponse({'error': gettext('No credential provided')}, status=400)

            return await handle_oauth_login(
                request=request,
                token=token,
                provider=self.provider,
                name=data.get('name'),
                surname=data.get('surname'),
                role=data.get('role'),
                phone_number=data.get('phone_number'),
                email_notifications=data.get('email_notifications', True),
                push_notifications=data.get('push_notifications', True),
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class GoogleAuthView(BaseAuthView):
    provider = "google"


class FacebookAuthView(BaseAuthView):
    provider = "facebook"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ForgotPasswordView(LocalizedView):
    @staticmethod
    async def post(request):
        try:
            data = json.loads(request.body)
            email = data['email']

            if not email:
                return error_response(gettext('No email address provided.'))

            try:
                await cached_email_validator(email)
            except ValidationError as e:
                return error_response(str(e))

            cache_key = f"forgot_reset_{hash(email)}"
            if await sync_to_async(cache.get)(cache_key):
                return error_response(
                    message=gettext(
                        'A password reset request has been sent. Please check your email or try again in 5 minutes.'),
                    status=429
                )

            user_data = await get_user_existence_cache(email)

            if not user_data['exists']:
                return error_response(gettext('No user with this email address was found.'), 404)

            if not user_data['is_active']:
                return error_response(gettext('Account is inactive.'), 400)

            if not user_data['is_verified']:
                return error_response(gettext('Email not confirmed. Please check your email.'), 400)

            user = await sync_to_async(CustomUser.objects.get)(email=email)
            await send_password_reset_email(user)

            await sync_to_async(cache.set)(cache_key, True, timeout=5 * 60)

            return success_response({"message": gettext('Please check your email for a password reset link.')})
        except KeyError:
            return error_response(gettext('Missing field: email'), 400)
        except json.JSONDecodeError:
            return error_response(gettext('Invalid JSON format.'), 400)
        except Exception as e:
            return error_response(f"{gettext('Error processing request:')} {str(e)}", 500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ResetPasswordView(LocalizedView):
    @staticmethod
    async def get(request):
        token = request.GET.get('token')

        if not token:
            return error_response(gettext('No token to reset the password.'), 400)

        try:
            email = signer.unsign(token, max_age=60 * 60 * 24)
            try:
                await sync_to_async(CustomUser.objects.get)(email=email)
                return redirect(f"{settings.FRONTEND_URL}/reset-password?token={token}")
            except CustomUser.DoesNotExist:
                return error_response(gettext('No user with this email address was found.'), 404)
        except SignatureExpired:
            return error_response(gettext('The token for resetting the password has expired.'), 400)
        except BadSignature:
            return error_response(gettext('Invalid token for password reset.'), 400)

    @staticmethod
    async def post(request):
        try:
            data = json.loads(request.body)

            if 'token' not in data or 'password' not in data:
                return error_response(gettext('Required fields are missing: token or password.'))

            token = data['token']
            password = data['password']

            try:
                await sync_to_async(validate_password)(password)
            except ValidationError as e:
                return error_response(', '.join(e.messages))

            try:
                email = signer.unsign(token, max_age=60 * 60 * 24)
                try:
                    user = await sync_to_async(CustomUser.objects.get)(email=email)
                    await sync_to_async(user.set_password)(password)
                    await sync_to_async(user.save)()

                    await invalidate_all_user_caches(user.id, user.email)

                    return success_response({"message": gettext('Password reset successful.')})
                except CustomUser.DoesNotExist:
                    return error_response(gettext('No user with this email address was found.'), 404)
            except SignatureExpired:
                return error_response(gettext('The token for resetting the password has expired.'), 400)
            except BadSignature:
                return error_response(gettext('Invalid token for password reset.'), 400)
        except json.JSONDecodeError:
            return error_response(gettext('Invalid JSON format.'), 400)
        except Exception as e:
            return error_response(f"{gettext('Error when resetting password:')} {str(e)}", 500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class LogoutView(LocalizedView):
    @login_required_async
    async def post(self, request):
        await sync_to_async(logout)(request)
        return success_response({"message": gettext('You have successfully logged out.')})


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ChangePasswordView(LocalizedView):
    @login_required_async
    async def patch(self, request):
        try:
            data = json.loads(request.body)

            if 'current_password' not in data or 'new_password' not in data or 'confirm_password' not in data:
                return error_response(
                    gettext('Required fields are missing: current_password, new_password, or confirm_password.'))

            current_password = data['current_password']
            new_password = data['new_password']
            confirm_password = data['confirm_password']

            if new_password != confirm_password:
                return error_response(gettext('The new password and password confirmation do not match.'), 400)

            try:
                await sync_to_async(validate_password)(new_password)
            except ValidationError as e:
                return error_response(', '.join(e.messages))

            user = request.user
            if not user.check_password(current_password):
                return error_response(gettext('Incorrect current password.'), 400)

            await sync_to_async(user.set_password)(new_password)
            await sync_to_async(user.save)()

            await invalidate_user_cache(user.id)

            await sync_to_async(login)(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return success_response({"message": gettext('Password successfully changed.')})
        except json.JSONDecodeError:
            return error_response(gettext('Invalid JSON format.'), 400)
        except Exception as e:
            return error_response(f"{gettext('Error when changing password:')} {str(e)}", 500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ProfileView(LocalizedView):
    @login_required_async
    async def get(self, request):
        try:
            profile_data = await get_cached_profile(request.user)
            return success_response(profile_data)
        except Exception as e:
            return error_response(f"{gettext('Error retrieving profile:')} {str(e)}", 500)

    @login_required_async
    async def post(self, request):
        """Separate endpoint for uploading avatars"""
        try:
            if 'profile_picture' not in request.FILES:
                return error_response(gettext('File not found.'), 400)

            profile_picture = request.FILES['profile_picture']
            user_profile, _ = await sync_to_async(UserProfile.objects.get_or_create)(user=request.user)

            await handle_picture(instance=user_profile,
                                 picture=profile_picture,
                                 instance_type="user",
                                 picture_field="profile_picture"
                                 )
            await invalidate_user_cache(await sync_to_async(lambda: request.user.id)())

            return success_response({
                "url": user_profile.profile_picture,
                "message": gettext('Avatar successfully uploaded.')
            })

        except ValidationError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f"{gettext('Error loading avatar:')} {str(e)}", 500)

    @login_required_async
    async def patch(self, request):
        try:
            data, is_multipart = parse_request_data(request)
            user = request.user

            await update_user_data(user, data.get('user', {}))
            await update_user_settings(user, data.get('settings', {}), is_multipart)
            await update_user_profile(user, data.get('profile', {}))

            await invalidate_user_cache(await sync_to_async(lambda: user.id)())
            updated_profile_data = await get_cached_profile(user)

            return success_response({
                "message": gettext('Profile successfully updated.'),
                "profile_data": updated_profile_data
            })

        except json.JSONDecodeError:
            return error_response(gettext('Invalid JSON format.'), 400)
        except ValidationError as e:
            if "NoSQL injection" in str(e):
                return error_response(str(e), 400)
            else:
                return error_response(str(e), 400)
        except Exception as e:
            return error_response(f"{gettext('Error updating profile:')} {str(e)}", 500)

    @login_required_async
    async def delete(self, request):
        try:
            user = request.user
            user_id = await sync_to_async(lambda: user.id)()
            user_email = await sync_to_async(lambda: user.email)()

            await sync_to_async(logout)(request)
            await delete_picture(
                instance_id=user_id,
                instance_type="user",
                delete_folder=True
            )
            await sync_to_async(user.delete)()

            await invalidate_all_user_caches(user_id, user_email)

            return success_response({"message": gettext('Your account has been successfully deleted.')})
        except Exception as e:
            return error_response(f"{gettext('Error when deleting an account:')} {str(e)}", 500)
