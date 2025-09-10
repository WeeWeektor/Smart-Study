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

    validate_category(data.get("category"))
    validate_level(data.get("level"))


def validate_category(category):
    """Валідатор для категорії"""
    if category not in VALID_CATEGORIES_CHOICES:
        raise ValidationError(
            _(f"Invalid category: '{category}'. Must be one of {', '.join(VALID_CATEGORIES_CHOICES)}.")
        )


def validate_level(level):
    """Валідатор для рівня"""
    if level and level not in VALID_CATEGORY_LEVELS:
        raise ValidationError(
            _(f"Invalid level: '{level}'. Must be one of {', '.join(VALID_CATEGORY_LEVELS)}.")
        )
