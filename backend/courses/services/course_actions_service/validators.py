from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

from courses.choices import VALID_CATEGORIES_CHOICES
from courses.utils import validate_choice


def validate_course_data(data):
    """Валідатор для даних курсу"""

    required_fields = ["title", "description", "category"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"{_('Missing required field:')} {field}")

    category_error = validate_choice(data.get("category"), VALID_CATEGORIES_CHOICES, _("category"))
    if category_error:
        raise ValidationError(category_error)

    if data.get("is_published", False):
        extra_fields = ["cover_image", "level", "course_language"]
        for field in extra_fields:
            if not data.get(field):
                raise ValidationError(f"{_('Missing required field for publish:')} {field}")
