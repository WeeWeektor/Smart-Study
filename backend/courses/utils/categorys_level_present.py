from django.core.exceptions import ValidationError

from common.utils import sanitize_input
from courses.services import validate_category, validate_level


def categories_level_present(request) -> list:
    """Повертає список категорій та рівнів для фільтрації курсів і тестів"""
    categories = request.GET.get('cate')
    level = request.GET.get('level')

    if categories:
        filter_list = [c.strip() for c in categories.split(",")]
        for f in filter_list:
            try:
                validate_category(f)
            except ValidationError:
                raise ValidationError(f"Invalid category: {f}")
    else:
        filter_list = ['all']
    if level:
        try:
            validate_level(level)
        except ValidationError:
            raise ValidationError(f"Invalid level: {level}")
        filter_list.append(level)

    filter_list = sanitize_input(filter_list)

    return filter_list
