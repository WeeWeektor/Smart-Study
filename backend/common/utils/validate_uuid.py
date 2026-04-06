import uuid
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

def validate_uuid(value: str) -> uuid.UUID:
    """Перевіряє, що рядок є валідним UUID, і повертає UUID-об'єкт"""

    if isinstance(value, uuid.UUID):
        return value

    if isinstance(value, str):
        value = value.strip()
        try:
            return uuid.UUID(value)
        except (ValueError, TypeError):
            raise ValidationError(_("Invalid UUID format"))

    raise ValidationError(_("Invalid UUID type"))
