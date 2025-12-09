import magic
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_PICTURE_FILE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_FILE_SIZE = 50 * 1024 * 1024  # На фронті обмеження 300МБ
MAX_DOCUMENT_FILE_SIZE = 20 * 1024 * 1024
MAX_PRESENTATION_FILE_SIZE = 50 * 1024 * 1024
MAX_AUDIO_FILE_SIZE = 10 * 1024 * 1024

SIG_ZIP = b'\x50\x4B\x03\x04'
SIG_OLE2 = b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'

ALLOWED_PICTURE_TYPES = {
    'image/jpeg': [b'\xff\xd8\xff'],
    'image/png': [b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'],
    'image/gif': [b'\x47\x49\x46\x38\x37\x61', b'\x47\x49\x46\x38\x39\x61'],
    'image/webp': [b'\x52\x49\x46\x46', b'\x57\x45\x42\x50'],
}

ALLOWED_VIDEO_TYPES = {
    'video/mp4': [b'\x00\x00\x00', b'\x66\x74\x79\x70'],
    'video/quicktime': [b'\x00\x00\x00', b'\x66\x74\x79\x70'],
    'video/x-msvideo': [b'\x52\x49\x46\x46'],
    'video/webm': [b'\x1A\x45\xDF\xA3'],
    'video/mpeg': [b'\x00\x00\x01\xBA', b'\x00\x00\x01\xB3'],
}

ALLOWED_AUDIO_TYPES = {
    'audio/mpeg': [b'\x49\x44\x33', b'\xFF\xFB', b'\xFF\xF3', b'\xFF\xF2'],
    'audio/wav': [b'\x52\x49\x46\x46'],
    'audio/ogg': [b'\x4F\x67\x67\x53'],
    'audio/mp4': [b'\x00\x00\x00'],
    'audio/x-m4a': [b'\x00\x00\x00'],
}

ALLOWED_DOCUMENT_TYPES = {
    'application/pdf': [b'\x25\x50\x44\x46'],
    'text/plain': [],
    'application/msword': [SIG_OLE2],
    'application/vnd.ms-excel': [SIG_OLE2],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [SIG_ZIP],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': [SIG_ZIP],
}

ALLOWED_PRESENTATION_TYPES = {
    'application/vnd.ms-powerpoint': [SIG_OLE2],
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': [SIG_ZIP],
    'application/vnd.oasis.opendocument.presentation': [SIG_ZIP],
    'application/x-iwork-keynote-sffkey': [SIG_ZIP, b'\x00\x00\x00'],
}

DANGEROUS_EXTENSIONS = [
    '.php', '.asp', '.aspx', '.jsp', '.exe', '.bat', '.cmd', '.sh', '.py', '.pl', '.cgi', '.jar',
    '.zip', '.rar', '.7z', '.tar', '.gz', '.iso'
]


def _check_dangerous_extension(filename):
    filename_lower = filename.lower()
    for ext in DANGEROUS_EXTENSIONS:
        if filename_lower.endswith(ext):
            raise ValidationError(_('File extension not allowed.'))


def _get_real_mime_type(file):
    file.seek(0)
    file_header = file.read(2048)
    file.seek(0)
    try:
        mime = magic.from_buffer(file_header, mime=True)
        return mime
    except Exception:
        return None


def validate_file_generic(file, max_size, allowed_types_map):
    if file.size > max_size:
        max_mb = max_size / (1024 * 1024)
        raise ValidationError(_(f'File too large. Maximum size: {int(max_mb)}MB'))

    _check_dangerous_extension(file.name)

    real_mime_type = _get_real_mime_type(file)

    valid_mimes = allowed_types_map.keys()

    if real_mime_type not in valid_mimes:
        raise ValidationError(_(f'File type not allowed. Detected: {real_mime_type}'))

    expected_signatures = allowed_types_map.get(real_mime_type, [])

    if not expected_signatures:
        return True

    file.seek(0)
    file_header = file.read(32)
    file.seek(0)

    valid_signature = False
    for signature in expected_signatures:
        if file_header.startswith(signature):
            valid_signature = True
            break

    if not valid_signature:
        if real_mime_type in ['video/mp4', 'video/quicktime'] and len(file_header) >= 12:
            if file_header[4:8] == b'ftyp':
                return True

        raise ValidationError(_('File signature does not match declared type'))

    return True

def validate_picture_file(file):
    return validate_file_generic(file, MAX_PICTURE_FILE_SIZE, ALLOWED_PICTURE_TYPES)


def validate_video_file(file):
    return validate_file_generic(file, MAX_VIDEO_FILE_SIZE, ALLOWED_VIDEO_TYPES)


def validate_audio_file(file):
    return validate_file_generic(file, MAX_AUDIO_FILE_SIZE, ALLOWED_AUDIO_TYPES)


def validate_document_file(file):
    return validate_file_generic(file, MAX_DOCUMENT_FILE_SIZE, ALLOWED_DOCUMENT_TYPES)


def validate_presentation_file(file):
    return validate_file_generic(file, MAX_PRESENTATION_FILE_SIZE, ALLOWED_PRESENTATION_TYPES)
