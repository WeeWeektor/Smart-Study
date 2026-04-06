import hashlib

from django.core.exceptions import ValidationError, PermissionDenied

from courses.models import Certificate
from .generate_certificate_file import generate_certificate_file


async def get_validated_certificate(user, certificate_id):
    try:
        certificate = await Certificate.objects.select_related('user', 'course').aget(certificate_id=certificate_id)
    except Certificate.DoesNotExist:
        raise

    if certificate.user_id != user.id:
        raise PermissionDenied("You do not have permission to download this certificate.")

    return certificate


def calculate_certificate_etag(certificate, fmt: str) -> str:
    """
    Генерує унікальний хеш на основі даних, які відображаються у сертифікаті.
    Якщо хоча б одне поле зміниться - хеш буде іншим.
    """
    data_to_hash = (
        f"{certificate.certificate_id}-"
        f"{certificate.user.name}-"
        f"{certificate.user.surname}-"
        f"{certificate.course.title}-"
        f"{fmt}"
    )
    return hashlib.md5(data_to_hash.encode('utf-8')).hexdigest()


async def generate_certificate_response_data(fmt: str, certificate):
    if fmt not in ['pdf', 'png']:
        raise ValidationError("Invalid format. Supported formats are 'pdf' and 'png'.")

    file_buffer = await generate_certificate_file(certificate, fmt)
    if not file_buffer:
        raise Exception("Error generating file buffer")

    ext = fmt
    content_type = 'application/pdf' if fmt == 'pdf' else 'image/png'
    filename = f"Certificate_{certificate.certificate_id}.{ext}"

    return file_buffer, filename, content_type
