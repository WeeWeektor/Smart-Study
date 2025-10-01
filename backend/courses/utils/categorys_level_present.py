from django.core.exceptions import ValidationError

from courses.services import validate_choice
from courses.choices import VALID_CATEGORIES_CHOICES, VALID_CATEGORY_LEVELS, VALID_SORTING_OPTIONS


def categories_level_sort_present(request) -> list | None and str | None and list | None:
    """Повертає список категорій та рівнів для фільтрації курсів і тестів"""
    categories = request.GET.get('cate')
    level = request.GET.get('level')
    sort_keys = request.GET.get('sort')

    category_list = _validate_list_param(categories, VALID_CATEGORIES_CHOICES, "category")
    sort_list = _validate_list_param(sort_keys, VALID_SORTING_OPTIONS, "sort option")

    if level:
        _call_validate_choice(level, VALID_CATEGORY_LEVELS, "level")

    return category_list, level, sort_list


def _validate_list_param(param: str, valid_choices: set, param_name: str) -> list[str] | None:
    """
       Перевіряє, чи всі значення param присутні в valid_choices.
       Повертає список значень або None.
    """
    if not param:
        return None

    values = [v.strip() for v in param.split(",")]

    for v in values:
        _call_validate_choice(v, valid_choices, param_name)
    return values


def _call_validate_choice(values: str, valid_choices: set, param_name: str):
    try:
        validate_choice(values, valid_choices, param_name)
    except ValidationError:
        raise ValidationError(f"Invalid {param_name}: {values}")
