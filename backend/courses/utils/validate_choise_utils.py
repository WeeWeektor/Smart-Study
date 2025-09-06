from django.utils.translation import gettext as _

from common.utils import error_response


def validate_choice(value: str, valid_set: set, field_name: str):
    if value not in valid_set:
        return error_response(
            _(f"Invalid {field_name}: '{value}'. Must be one of {', '.join(valid_set)}."),
            status=400
        )
    return None
