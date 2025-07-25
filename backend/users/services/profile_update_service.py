from django.core.exceptions import ValidationError
from ..models import UserSettings, UserProfile
from ..utils.validators import phone_validator


def update_user_data(user, data):
    if 'name' in data and data['name'].strip():
        user.name = data['name']
    if 'surname' in data and data['surname'].strip():
        user.surname = data['surname']
    if 'phone_number' in data:
        try:
            if data['phone_number'] is None or data['phone_number'].strip() == '':
                user.phone_number = None
            else:
                phone_validator(data['phone_number'])
                user.phone_number = data['phone_number']
        except ValidationError as e:
            raise ValidationError(str(e))
    user.save()


def update_user_settings(user, data, is_multipart=False):
    user_settings, _ = UserSettings.objects.get_or_create(user=user)
    settings_fields = ['email_notifications', 'push_notifications', 'deadline_reminders',
                       'show_profile_to_others', 'show_achievements']
    for field in settings_fields:
        if field in data:
            if is_multipart:
                setattr(user_settings, field, data[field].lower() == 'true')
            else:
                setattr(user_settings, field, data[field])
    user_settings.save()


def update_user_profile(user, data):
    user_profile, _ = UserProfile.objects.get_or_create(user=user)
    profile_fields = ['bio', 'location', 'organization', 'specialization', 'education_level']
    for field in profile_fields:
        if field in data:
            setattr(user_profile, field, data[field])
    user_profile.save()
