from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.models import Certificate
from courses.services.certificate_actions_service import create_certificate, generate_certificate_file


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CertificateView(LocalizedView):
    @login_required_async
    async def post(self, request, course_id):
        user_id = request.user.id

        try:
            certificate, created = await create_certificate(course_id, user_id)

            status_code = 201 if created else 200
            message = gettext("Certificate created successfully.") if created else gettext("Certificate already exist.")

            return success_response({
                "message": message,
                "course_id": str(course_id),
                "id": str(certificate.id),
                "certificate_id": str(certificate.certificate_id),
                "issued_at": str(certificate.issued_at),
                "is_valid": certificate.is_valid
            }, status=status_code)
        except ObjectDoesNotExist:
            return error_response(gettext("Course not found."), status=404)
        except ValidationError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response(gettext(f"Error issuing certificate: {str(e)}"), status=500)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class DownloadCertificateView(LocalizedView):
    @login_required_async
    async def get(self, request, certificate_id):
        try:
            certificate = await Certificate.objects.select_related('user', 'course').aget(certificate_id=certificate_id)

            if certificate.user_id != request.user.id:
                return error_response(gettext("You do not have permission to download this certificate."), status=403)

            fmt = request.GET.get('format', 'pdf').lower()

            if fmt not in ['pdf', 'png']:
                return error_response(gettext("Invalid format. Supported formats are 'pdf' and 'png'."), status=400)

            file_buffer = await generate_certificate_file(certificate, fmt)

            if not file_buffer:
                return error_response(gettext("Error generating file."), status=500)

            if fmt == 'pdf':
                content_type = 'application/pdf'
                filename = f"Certificate_{certificate.certificate_id}.pdf"
            else:
                content_type = 'image/png'
                filename = f"Certificate_{certificate.certificate_id}.png"

            response = HttpResponse(file_buffer, content_type=content_type)

            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Certificate.DoesNotExist:
            return error_response(gettext("Certificate not found."), status=404)
        except Exception as e:
            return error_response(gettext(f"Server error: {str(e)}"), status=500)
