from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from courses.choices import VALID_CATEGORIES_CHOICES, VALID_CATEGORY_LEVELS


def validate_course_data(data):
    """Валідатор для даних курсу"""

    required_fields = ["title", "description", "category"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"{_('Missing required field:')} {field}")

    if data.get("is_published", False):
        extra_fields = ["level", "course_language", "time_to_complete"]
        for field in extra_fields:
            if not data.get(field):
                raise ValidationError(f"{_('Missing required field for publish:')} {field}")

    validate_category_level(data)


def validate_choice(choice: str, valid_choices: set, name: str) -> None:
    """Валідатор для вибору"""
    if choice and choice not in valid_choices:
        raise ValidationError(
            _(f"Invalid {name}: '{choice}'. Must be one of {', '.join(valid_choices)}.")
        )


def validate_category_level(data: dict):
    """Валідатор для категорії та рівня"""
    if category := data.get("category"):
        validate_choice(category, VALID_CATEGORIES_CHOICES, "category")
    if level := data.get("level"):
        validate_choice(level, VALID_CATEGORY_LEVELS, "level")
