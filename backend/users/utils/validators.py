from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.utils.translation import gettext

email_validator = EmailValidator(message=gettext('Incorrect email format.'))

phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{10,15}$',
    message=gettext('The phone number must contain between 10 and 15 digits, including the prefix.')
)

def cached_email_validator(email):
    """Cached email validator to reduce load"""
    cache_key = f"email_valid_{hash(email)}"
    is_valid = cache.get(cache_key)

    if is_valid is None:
        try:
            email_validator(email)
            is_valid = True
        except ValidationError:
            is_valid = False
        cache.set(cache_key, is_valid, timeout=30*60)

    if not is_valid:
        raise ValidationError(gettext('Incorrect email format.'))

    return True
