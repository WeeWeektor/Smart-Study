from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from common.utils import error_response
from courses.choices import VALID_CATEGORIES_CHOICES, VALID_CATEGORY_LEVELS


def validate_course_data(data):
    """Валідатор для даних курсу"""

    required_fields = ["title", "description", "category"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"{_('Missing required field:')} {field}")

    if data.get("is_published", False):
        extra_fields = ["cover_image", "level", "course_language", "time_to_complete"]
        for field in extra_fields:
            if not data.get(field):
                raise ValidationError(f"{_('Missing required field for publish:')} {field}")

    validate_category(data.get("category"))
    validate_level(data.get("level"))


def validate_category(category):
    """Валідатор для категорії"""

    category_error = validate_choice(category, VALID_CATEGORIES_CHOICES, _("category"))
    if category_error:
        raise ValidationError(category_error)


def validate_level(level):
    """Валідатор для рівня"""

    level_error = validate_choice(level, VALID_CATEGORY_LEVELS, _("level"))
    if level_error:
        raise ValidationError(level_error)


def validate_choice(value: str, valid_set: set, field_name: str):
    if value not in valid_set:
        return error_response(
            _(f"Invalid {field_name}: '{value}'. Must be one of {', '.join(valid_set)}."),
            status=400
        )
    return None
