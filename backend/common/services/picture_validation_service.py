import magic
from django.core.exceptions import ValidationError
from django.utils.translation import gettext

ALLOWED_FILE_TYPES = {
    'image/jpeg': [b'\xff\xd8\xff'],
    'image/png': [b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'],
    'image/gif': [b'\x47\x49\x46\x38\x37\x61', b'\x47\x49\x46\x38\x39\x61'],
    'image/webp': [b'\x52\x49\x46\x46', b'\x57\x45\x42\x50'],
}

MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_picture_file_security(file):
    """Валідація безпеки файлу"""

    if file.size > MAX_FILE_SIZE:
        raise ValidationError(gettext('File too large. Maximum size: 5MB'))

    file.seek(0)
    file_header = file.read(32)
    file.seek(0)

    try:
        real_mime_type = magic.from_buffer(file_header, mime=True)
    except:
        real_mime_type = None

    declared_mime_type = file.content_type

    if declared_mime_type not in ALLOWED_FILE_TYPES:
        raise ValidationError(gettext('File type not allowed. Allowed types: JPEG, PNG, GIF, WebP'))

    valid_signature = False
    for signature in ALLOWED_FILE_TYPES[declared_mime_type]:
        if file_header.startswith(signature):
            valid_signature = True
            break

    if not valid_signature:
        raise ValidationError(gettext('File signature does not match declared type'))

    if real_mime_type and real_mime_type != declared_mime_type:
        raise ValidationError(gettext('Content-Type spoofing detected'))

    dangerous_extensions = ['.php', '.asp', '.jsp', '.exe', '.bat', '.cmd', '.sh']
    filename_lower = file.name.lower()

    for ext in dangerous_extensions:
        if ext in filename_lower:
            raise ValidationError(gettext('Dangerous file extension detected'))

    return True
