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


def validate_module_data(data: dict):
    """Валідатор для даних модуля"""

    validate_required_fields(data, ["title", "order"])
    validate_positive_int(data.get("order"), "order")


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


def validate_list_of_strings(lst: list[str], field_name: str) -> None:
    if not isinstance(lst, list) or not all(isinstance(item, str) for item in lst):
        raise ValidationError(_(f"{field_name} must be a list of strings"))


def validate_positive_int(value, field_name: str) -> None:
    if value is not None and (not isinstance(value, int) or value < 1):
        raise ValidationError(_(f"{field_name} must be integer >= 1"))


def validate_test_question_data(q):
    question_text = q.get("questionText")
    if not isinstance(question_text, str) or not question_text.strip():
        raise ValueError(_("question text must be a non-empty string"))

    choices = q.get("choices", [])
    correct_answers = q.get("correctAnswers", [])

    validate_list_of_strings(choices, "choices")
    validate_list_of_strings(correct_answers, "correctAnswers")

    if not all(answer in choices for answer in correct_answers):
        raise ValidationError(_("All correct answers must be present in choices"))

    validate_positive_int(q.get("points", 1), "points")
    validate_positive_int(q.get("order"), "order")
