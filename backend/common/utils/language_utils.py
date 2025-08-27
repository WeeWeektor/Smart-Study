from smartStudy_backend import settings


def get_language_from_request(request):
    cookie_lang = request.COOKIES.get('django_language') or request.COOKIES.get('language')
    if cookie_lang:
        return cookie_lang

    x_language = request.headers.get('X-Language')
    if x_language:
        return x_language

    x_req_language = request.headers.get('X-Request-Language')
    if x_req_language:
        return x_req_language

    lang_param = request.GET.get('lang')
    if lang_param:
        return lang_param

    if request.method == 'POST':
        lang_post = request.POST.get('lang')
        if lang_post:
            return lang_post

    accept_lang = parce_accept_language(request.headers.get('Accept-Language', ''))
    if accept_lang:
        return accept_lang

    return getattr(settings, 'LANGUAGE_CODE', 'en')


def parce_accept_language(accept_language_header):
    if not accept_language_header:
        return None

    languages = []
    for lang_item in accept_language_header.split(','):
        lang_item = lang_item.strip()
        lang_code = lang_item.split(';')[0].split('-')[0].lower()
        languages.append(lang_code)

    unique_languages = list(set(languages))
    for lang_code in unique_languages:
        if lang_code in [lang[0] for lang in settings.LANGUAGES]:
            return lang_code

    return None


def validate_language(language):
    if not language:
        return getattr(settings, 'LANGUAGE_CODE', 'en')

    if language not in [lang[0] for lang in settings.LANGUAGES]:
        return getattr(settings, 'LANGUAGE_CODE', 'en')
    else:
        return language
