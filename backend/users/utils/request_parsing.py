import json

def parse_request_data(request):
    """Парсинг даних запиту: повертає (data, is_multipart)"""
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        return request.POST.dict(), True
    else:
        return json.loads(request.body), False
