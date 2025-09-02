from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError

from common.utils import sanitize_input
from ..models import UserSettings, UserProfile
from ..utils.validators import phone_validator


async def update_user_data(user, data):
    forbidden_fields = ['role', 'is_staff', 'is_superuser', 'is_active', 'is_verified_email']

    if not user.is_staff:
        for field in forbidden_fields:
            data.pop(field, None)

    if 'name' in data and data['name']:
        if len(data['name'].strip()) > 100:
            raise ValidationError("Name too long")
        user.name = sanitize_input(data['name'])
    if 'surname' in data and data['surname']:
        if len(data['surname'].strip()) > 100:
            raise ValidationError("Surname too long")
        user.surname = sanitize_input(data['surname'])
    if 'phone_number' in data:
        try:
            if data['phone_number'] is None or data['phone_number'].strip() == '':
                user.phone_number = None
            else:
                phone_validator(data['phone_number'])
                user.phone_number = data['phone_number']
        except ValidationError as e:
            raise ValidationError(str(e))
    await sync_to_async(user.save)()


async def update_user_settings(user, data, is_multipart=False):
    user_settings, _ = await sync_to_async(UserSettings.objects.get_or_create)(user=user)
    settings_fields = ['email_notifications', 'push_notifications', 'deadline_reminders',
                       'show_profile_to_others', 'show_achievements']
    for field in settings_fields:
        if field in data:
            if is_multipart:
                setattr(user_settings, field, data[field].lower() == 'true')
            else:
                setattr(user_settings, field, data[field])
    await sync_to_async(user_settings.save)()


async def update_user_profile(user, data):
    user_profile, _ = await sync_to_async(UserProfile.objects.get_or_create)(user=user)
    profile_fields = ['bio', 'location', 'organization', 'specialization', 'education_level']
    for field in profile_fields:
        if field in data:
            value = data[field]
            if value is not None and str(value).strip():
                sanitized_value = sanitize_input(value)
                setattr(user_profile, field, sanitized_value if sanitized_value else None)
            else:
                setattr(user_profile, field, None)
    await sync_to_async(user_profile.save)()
