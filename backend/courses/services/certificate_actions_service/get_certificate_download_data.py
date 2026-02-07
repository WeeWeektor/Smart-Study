from django.core.exceptions import ValidationError, PermissionDenied
from .generate_certificate_file import generate_certificate_file

from courses.models import Certificate


async def get_certificate_download_data(fmt: str, certificate_id: str, user):
    if fmt not in ['pdf', 'png']:
        raise ValidationError("Invalid format. Supported formats are 'pdf' and 'png'.")

    try:
        certificate = await Certificate.objects.select_related('user', 'course').aget(certificate_id=certificate_id)
    except Certificate.DoesNotExist:
        raise

    if certificate.user_id != user.id:
        raise PermissionDenied("You do not have permission to download this certificate.")

    file_buffer = await generate_certificate_file(certificate, fmt)
    if not file_buffer:
        raise Exception("Error generating file buffer")

    ext = fmt
    content_type = 'application/pdf' if fmt == 'pdf' else 'image/png'
    filename = f"Certificate_{certificate.certificate_id}.{ext}"

    return file_buffer, filename, content_type, certificate
