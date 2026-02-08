from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse, HttpResponseNotModified
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.models import Certificate
from courses.services.certificate_actions_service import create_certificate, generate_certificate_response_data, \
    get_validated_certificate, calculate_certificate_etag


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
            certificate = await get_validated_certificate(request.user, certificate_id)

            etag = calculate_certificate_etag(certificate, fmt)
            if_none_match = request.META.get('HTTP_IF_NONE_MATCH')

            if if_none_match == etag:
                return HttpResponseNotModified()

            file_buffer, filename, content_type = await generate_certificate_response_data(fmt, certificate)

            response = HttpResponse(file_buffer, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            response['Etag'] = etag
            response['Cache-Control'] = 'private, must-revalidate, max-age=3600'

            response['Access-Control-Expose-Headers'] = 'Etag, Content-Disposition'

            return response

        except ValidationError as e:
            return error_response(str(e), status=400)
        except PermissionDenied as e:
            return error_response(str(e), status=403)
        except Certificate.DoesNotExist:
            return error_response(gettext("Certificate not found."), status=404)
        except Exception as e:
            return error_response(gettext(f"Server error: {str(e)}"), status=500)
