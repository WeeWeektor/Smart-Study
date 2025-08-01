from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.core.cache import cache

email_validator = EmailValidator(message='Некоректний формат електронної пошти.')

phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{10,15}$',
    message='Номер телефону має містити від 10 до 15 цифр, з префіксом.'
)

def cached_email_validator(email):
    """Кешований валідатор email для зменшення навантаження"""
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
        raise ValidationError('Некоректний формат електронної пошти.')

    return True
