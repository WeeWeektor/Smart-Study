from django.core.exceptions import ValidationError

from courses.services import validate_category, validate_level


def categories_level_present(request) -> list | None and str | None:
    """Повертає список категорій та рівнів для фільтрації курсів і тестів"""
    categories = request.GET.get('cate')
    level = request.GET.get('level')

    if categories:
        category_list = [c.strip() for c in categories.split(",")]
        for f in category_list:
            try:
                validate_category(f)
            except ValidationError:
                raise ValidationError(f"Invalid category: {f}")
    else:
        category_list = None

    if level:
        try:
            validate_level(level)
        except ValidationError:
            raise ValidationError(f"Invalid level: {level}")

    return category_list, level
