import re
from django.utils.html import strip_tags


def sanitize_input(value):
    """Санітизація користувацького вводу"""
    if not value:
        return value

    clean_value = strip_tags(value)

    dangerous_patterns = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'on\w+\s*=',
    ]

    for pattern in dangerous_patterns:
        clean_value = re.sub(pattern, '', clean_value, flags=re.IGNORECASE)

    return clean_value.strip()
