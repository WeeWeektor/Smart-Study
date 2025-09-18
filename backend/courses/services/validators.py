from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from courses.choices import VALID_CATEGORIES_CHOICES, VALID_CATEGORY_LEVELS


def validate_course_data(data: dict):
    """Валідатор для даних курсу"""

    validate_required_fields(data, ["title", "description", "category"])

    if data.get("is_published", False):
        validate_required_fields(data, ["level", "course_language", "time_to_complete"],
                                 msg=_("Missing required field for publish:"))

    validate_category_level(data)


def validate_test_data(data: dict, test_type: str):
    """Валідатор для даних тесту"""

    validate_required_fields(data, ["title", "description", "questions"])

    if test_type == "public":
        validate_required_fields(data, ["level", "category"],
                                 msg=_("Missing required field for public test:"))
        validate_category_level(data)
    else:
        validate_required_fields(data, ["order"],
                                 msg=_("Missing required field for course/module test:"))


def validate_required_fields(data: dict, required_fields: list[str], msg: str | None = None) -> None:
    """Перевірка наявності required полів"""
    if msg is None:
        msg = _("Missing required field:")

    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"{msg} {field}")



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
