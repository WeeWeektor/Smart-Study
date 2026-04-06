from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.utils.translation import gettext

email_validator = EmailValidator(message=gettext('Incorrect email format.'))

phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{10,15}$',
    message=gettext('The phone number must contain between 10 and 15 digits, including the prefix.')
)


async def cached_email_validator(email):
    """Cached email validator to reduce load"""
    cache_key = f"email_valid_{hash(email)}"
    is_valid = await sync_to_async(cache.get)(cache_key)

    if is_valid is None:
        try:
            await sync_to_async(email_validator)(email)
            is_valid = True
        except ValidationError:
            is_valid = False
        await sync_to_async(cache.set)(cache_key, is_valid, timeout=30 * 60)

    if not is_valid:
        raise ValidationError(gettext('Incorrect email format.'))

    return True
