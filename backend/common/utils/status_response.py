from django.utils.translation import gettext as _

from django.http import JsonResponse


def error_response(message, status=400):
    return JsonResponse({"status": "error", "message": message}, status=status)


def success_response(data=None, message=_('Successfully'), status=_("success")):
    response = {"status": status, "message": message}
    if data:
        response.update(data)
    return JsonResponse(response)
