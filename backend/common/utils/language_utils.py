from smartStudy_backend import settings


def get_language_from_request(request):
    cookie_lang = request.COOKIES.get('django_language') or request.COOKIES.get('language')
    if cookie_lang:
        return cookie_lang.lower()

    x_language = request.headers.get('X-Language')
    if x_language:
        return x_language.lower()

    x_req_language = request.headers.get('X-Request-Language')
    if x_req_language:
        return x_req_language.lower()

    lang_param = request.GET.get('lang')
    if lang_param:
        return lang_param.lower()

    if request.method == 'POST':
        lang_post = request.POST.get('lang')
        if lang_post:
            return lang_post.lower()

    accept_lang = parce_accept_language(request.headers.get('Accept-Language', ''))
    if accept_lang:
        return accept_lang.lower()

    return getattr(settings, 'LANGUAGE_CODE', 'en').lower()


def parce_accept_language(accept_language_header):
    if not accept_language_header:
        return None

    languages = []
    for lang_item in accept_language_header.split(','):
        lang_item = lang_item.strip()
        lang_code = lang_item.split(';')[0].split('-')[0].lower()
        if lang_code not in languages:
            languages.append(lang_code)

    for lang_code in languages:
        if lang_code in [lang[0] for lang in settings.LANGUAGES]:
            return lang_code.lower()

    return None


def validate_language(language):
    if not language:
        return getattr(settings, 'LANGUAGE_CODE', 'en').lower()

    if language.lower() not in [lang[0] for lang in settings.LANGUAGES]:
        return getattr(settings, 'LANGUAGE_CODE', 'en').lower()
    else:
        return language.lower()
