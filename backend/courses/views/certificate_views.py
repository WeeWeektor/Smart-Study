from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, success_response
from courses.services.certificate_actions_service import create_certificate


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
