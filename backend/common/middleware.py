from django.utils.translation import gettext
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from common.utils import get_language_from_request, validate_language
from smartStudy_backend import settings


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = get_language_from_request(request)
        language = validate_language(language)
        translation.activate(language)
        request.LANGUAGE_CODE = language

        response = self.get_response(request)

        if hasattr(response, 'set_cookie'):
            response.set_cookie(
                'django_language',
                language,
                max_age=365 * 24 * 60 * 60,
                httponly=False,
                samesite='Lax',
                secure=settings.SESSION_COOKIE_SECURE,
                path='/',
            )
            response['X-Current-Language'] = language

        translation.deactivate()
        return response


class RateLimitMiddleware(MiddlewareMixin):
    RATE_LIMIT_CONFIG = {
        '/api/auth/login/': {'max_attempts': 5, 'window': 300, 'key_prefix': 'login'},
        '/api/auth/register/': {'max_attempts': 3, 'window': 600, 'key_prefix': 'register'},
        '/api/auth/forgot-password/': {'max_attempts': 3, 'window': 300, 'key_prefix': 'forgot_password'},
        '/api/auth/reset-password/': {'max_attempts': 5, 'window': 300, 'key_prefix': 'reset_password'},
        '/api/user/change-password/': {'max_attempts': 3, 'window': 300, 'key_prefix': 'change_password'},
    }

    def process_request(self, request):
        if getattr(settings, 'DISABLE_RATE_LIMITING', False):
            return None
        try:
            if request.method in ['POST', 'PATCH']:
                config = self.get_rate_limit_config(request.path)

                if config:
                    ip = self.get_client_ip(request)
                    key = f"{config['key_prefix']}_attempts_{ip}"

                    attempts = cache.get(key, 0)
                    if attempts >= config['max_attempts']:
                        return JsonResponse(
                            {'error': gettext('Too many requests. Try again later.')},
                            status=429
                        )

                    request._rate_limit_key = key
                    request._rate_limit_config = config

        except Exception:
            pass

        return None

    @staticmethod
    def process_response(request, response):
        try:
            if hasattr(request, '_rate_limit_key') and hasattr(request, '_rate_limit_config'):
                key = request._rate_limit_key
                config = request._rate_limit_config

                if response.status_code >= 400:
                    attempts = cache.get(key, 0)
                    cache.set(key, attempts + 1, config['window'])
                elif response.status_code == 200:
                    cache.delete(key)

        except Exception:
            pass

        return response

    def get_rate_limit_config(self, path):
        for endpoint, config in self.RATE_LIMIT_CONFIG.items():
            if path.startswith(endpoint):
                return config
        return None

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class SessionSecurityMiddleware(MiddlewareMixin):
    PROTECTED_ENDPOINTS = [
        '/api/user/profile/',
        '/api/user/change-password/',
        '/admin/',
    ]

    def process_request(self, request):
        try:
            if not self.is_protected_endpoint(request.path):
                return None

            if request.user.is_authenticated:
                current_ip = self.get_client_ip(request)
                session_ip = request.session.get('ip_address')

                if session_ip and session_ip != current_ip:
                    if not self.is_local_ip_change(session_ip, current_ip):
                        request.session.flush()
                        return JsonResponse(
                            {'error': gettext('Session security violation. Please login again.')},
                            status=401
                        )

                request.session['ip_address'] = current_ip

        except Exception:
            pass

        return None

    def is_protected_endpoint(self, path):
        return any(path.startswith(endpoint) for endpoint in self.PROTECTED_ENDPOINTS)

    @staticmethod
    def is_local_ip_change(old_ip, new_ip):
        local_ips = ['127.0.0.1', 'localhost', '::1']
        return old_ip in local_ips and new_ip in local_ips

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    @staticmethod
    def process_response(request, response):
        if hasattr(response, '__setitem__'):
            response['X-Frame-Options'] = 'DENY'
            response['X-Content-Type-Options'] = 'nosniff'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        return response
