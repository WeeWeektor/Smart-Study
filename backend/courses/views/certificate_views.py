from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.http import http_date
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.models import Certificate
from courses.services.certificate_actions_service import create_certificate, get_certificate_download_data


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
        fmt = request.GET.get('format', 'pdf').lower()

        try:
            file_buffer, filename, content_type, certificate = await (
                get_certificate_download_data(fmt, certificate_id, request.user)
            )

            response = HttpResponse(file_buffer, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            last_modified = getattr(certificate, 'issued_at')
            response['Last-Modified'] = http_date(last_modified.timestamp())
            response['Cache-Control'] = 'private, max-age=3600'

            return response

        except ValidationError as e:
            return error_response(str(e), status=400)
        except PermissionDenied as e:
            return error_response(str(e), status=403)
        except Certificate.DoesNotExist:
            return error_response(gettext("Certificate not found."), status=404)
        except Exception as e:
            return error_response(gettext(f"Server error: {str(e)}"), status=500)
