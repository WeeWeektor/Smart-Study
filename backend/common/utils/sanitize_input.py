import re
import html
import unicodedata
from django.utils.translation import gettext
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError


def sanitize_input(value, multiline=False):
    """Санітизація користувацького вводу"""
    if value is None:
        return None

    sanitized = str(value)
    if not sanitized.strip():
        return None if value == '' else ''

    sanitized = strip_tags(sanitized)
    sanitized = unicodedata.normalize('NFKC', sanitized)

    allowed_control_chars = ['\n', '\r'] if multiline else []
    sanitized = ''.join(
        char for char in sanitized
        if unicodedata.category(char)[0] != 'C' or char in allowed_control_chars
    )
    
    nosql_patterns = [r'\$where', r'\$ne', r'\$gt', r'\$lt', r'\$regex', r'\$or', r'\$and', r'\$exists', r'\$in',
                      r'\$nin']
    for pattern in nosql_patterns:
        if re.search(pattern, sanitized, re.IGNORECASE):
            raise ValidationError(f"{gettext('NoSQL injection pattern detected: ')}{pattern}")

    dangerous_chars = [';', '|', '&', '`', '$', '\\']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')

    sql_patterns = [
        r'drop\s+table\s*[^;]*;?',
        r'delete\s+from\s*[^;]*;?',
        r'insert\s+into\s*[^;]*;?',
        r'update\s+.*set\s*[^;]*;?',
        r'select\s+.*from\s*[^;]*;?',
        r'union\s+select\s*[^;]*;?',
        r'alter\s+table\s*[^;]*;?',
        r'create\s+table\s*[^;]*;?',
        r'truncate\s+table\s*[^;]*;?',
        r'--.*$',
        r'/\*.*?\*/',
        r';\s*--',
    ]

    template_patterns = [
        r'\$\{jndi:.*?\}',
        r'\$\{.*?:.*?\}',
        r'\{\{.*?\}\}',
        r'\<%=.*?%\>',
        r'\{%.*?%\}',
        r'\{\{7\*7\}\}',
    ]

    xss_patterns = [
        r'<script.*?</script>',
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'on\w+\s*=',
        r'exec\s*\(',
        r'eval\s*\(',
    ]

    system_patterns = [
        r'rm\s+-rf',
        r'del\s+/[qfs]',
        r'format\s+[c-z]:',
        r'shutdown\s+',
        r'reboot\s*',
        r'cat\s+/',
    ]

    all_patterns = sql_patterns + template_patterns + xss_patterns + system_patterns
    for pattern in all_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)

    sanitized = html.escape(sanitized)

    if multiline:
        sanitized = re.sub(r'[ \t]+', ' ', sanitized)
        sanitized = re.sub(r'(\n\s*){3,}', '\n\n', sanitized)
    else:
        sanitized = re.sub(r'\s+', ' ', sanitized)

    return sanitized.strip() if sanitized else ''
