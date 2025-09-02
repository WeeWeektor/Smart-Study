import re
import html
import unicodedata
from gettext import gettext
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError


def sanitize_input(value):
    """Санітизація користувацького вводу"""
    if not value:
        return None

    sanitized = strip_tags(str(value))
    sanitized = unicodedata.normalize('NFKC', sanitized)
    sanitized = ''.join(char for char in sanitized if unicodedata.category(char)[0] != 'C')

    nosql_patterns = [r'\$where', r'\$ne', r'\$gt', r'\$lt', r'\$regex', r'\$or', r'\$and', r'\$exists', r'\$in',
                      r'\$nin']
    for pattern in nosql_patterns:
        if re.search(pattern, sanitized, re.IGNORECASE):
            raise ValidationError(f"{gettext('NoSQL injection pattern detected: ')}{pattern}")

    dangerous_chars = [';', '|', '&', '`', '$', '(', ')', '*', '\\']
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
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized if sanitized else ''
