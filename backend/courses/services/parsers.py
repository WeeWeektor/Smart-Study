import json
from django.utils.translation import gettext
from django.http.multipartparser import MultiPartParser, MultiPartParserError

from common.utils import error_response


def parse_multipart_request(request):
    """Парсинг multipart/form-data"""
    try:
        parser = MultiPartParser(
            request.META,
            request,
            request.upload_handlers
        )
        data, files = parser.parse()
    except MultiPartParserError as e:
        return None, None, error_response(f"{gettext('Error parsing multipart data:')} {str(e)}", status=400)

    raw_json = data.get('data', '{}')
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        data = {}

    return data, files, None
