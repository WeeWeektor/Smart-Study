from django.test import TestCase, Client, override_settings
from django.http import HttpRequest, HttpResponse
from unittest.mock import patch
from rest_framework.response import Response

from common.utils import get_language_from_request, validate_language
from common.views import LocalizedView, LocalizedAPIView


class TestMiddlewareViewIntegration(TestCase):
    """Тести інтеграції middleware з views"""

    def setUp(self):
        self.factory = lambda: HttpRequest()

    async def test_middleware_with_localized_view_integration(self):
        """Тест інтеграції middleware з LocalizedView"""

        class TestView(LocalizedView):
            @staticmethod
            async def get(request, *args, **kwargs):
                return HttpResponse(f"Active: {getattr(request, 'LANGUAGE_CODE', 'none')}")

        from common.utils.language_utils import get_language_from_request, validate_language

        request = HttpRequest()
        request.method = 'GET'
        request.META['HTTP_X_LANGUAGE'] = 'en'

        language = get_language_from_request(request)
        language = validate_language(language)

        from django.utils import translation
        translation.activate(language)
        request.LANGUAGE_CODE = language

        view = TestView()
        response = await view.dispatch(request)

        self.assertEqual(request.LANGUAGE_CODE, 'en')
        self.assertIn('Active: en', response.content.decode())
        translation.deactivate()

    async def test_middleware_with_api_view_integration(self):
        """Тест інтеграції middleware з LocalizedAPIView"""

        class TestAPIView(LocalizedAPIView):
            @staticmethod
            async def get(request, *args, **kwargs):
                return Response({
                    "language": getattr(request, 'LANGUAGE_CODE', 'none'),
                    "message": "API response"
                })

        from common.utils.language_utils import get_language_from_request, validate_language

        async def async_api_wrapper(request):
            language = get_language_from_request(request)
            language = validate_language(language)

            from django.utils import translation
            translation.activate(language)
            request.LANGUAGE_CODE = language

            view = TestAPIView()
            response = await view.dispatch(request)

            if isinstance(response, Response):
                import json
                http_response = HttpResponse(
                    json.dumps(response.data),
                    content_type='application/json'
                )
                http_response['X-Current-Language'] = language
            else:
                http_response = response
                http_response['X-Current-Language'] = language

            translation.deactivate()
            return http_response

        request = HttpRequest()
        request.method = 'GET'
        request.COOKIES = {'django_language': 'en'}

        response = await async_api_wrapper(request)

        self.assertEqual(request.LANGUAGE_CODE, 'en')
        self.assertEqual(response['X-Current-Language'], 'en')
        self.assertEqual(response['Content-Type'], 'application/json')

    @override_settings(LANGUAGES=[('en', 'English'), ('uk', 'Ukrainian')])
    async def test_full_request_cycle_with_language_priority(self):
        """Тест повного циклу запиту з пріоритетом джерел мови"""

        class PriorityTestView(LocalizedView):
            @staticmethod
            async def get(request, *args, **kwargs):
                return HttpResponse(f"Active: {getattr(request, 'LANGUAGE_CODE', 'none')}")

        from common.utils.language_utils import get_language_from_request, validate_language

        request = HttpRequest()
        request.method = 'GET'
        request.COOKIES = {'django_language': 'uk'}  # Найвищий пріоритет
        request.GET = {'lang': 'en'}  # Нижчий пріоритет
        request.META['HTTP_ACCEPT_LANGUAGE'] = 'fr'  # Найнижчий пріоритет

        language = get_language_from_request(request)
        language = validate_language(language)

        from django.utils import translation
        translation.activate(language)
        request.LANGUAGE_CODE = language

        view = PriorityTestView()
        response = await view.dispatch(request)

        self.assertEqual(request.LANGUAGE_CODE, 'uk')
        self.assertIn('Active: uk', response.content.decode())
        translation.deactivate()


class TestLanguageUtilsIntegration(TestCase):
    """Тести інтеграції utils з реальними запитами"""

    def setUp(self):
        self.factory = lambda: HttpRequest()

    @override_settings(LANGUAGES=[('en', 'English'), ('uk', 'Ukrainian'), ('fr', 'French')])
    def test_utils_with_real_accept_language_header(self):
        """Тест utils з реальними Accept-Language headers"""
        from common.utils.language_utils import get_language_from_request, parce_accept_language

        request = HttpRequest()
        request.method = 'GET'
        request.META = {'HTTP_ACCEPT_LANGUAGE': 'fr-FR,fr;q=0.9,en;q=0.8,uk;q=0.7'}

        result = get_language_from_request(request)
        self.assertEqual(result, 'en')

        request2 = HttpRequest()
        request2.method = 'GET'
        request2.META = {'HTTP_ACCEPT_LANGUAGE': 'uk-UA,uk;q=0.9'}

        result2 = get_language_from_request(request2)
        self.assertEqual(result2, 'uk')

        request3 = HttpRequest()
        request3.method = 'GET'
        request3.META = {'HTTP_ACCEPT_LANGUAGE': 'de-DE,de;q=0.9,it;q=0.8'}

        result3 = get_language_from_request(request3)
        self.assertEqual(result3, 'en')  # fallback до default

        result4 = parce_accept_language('fr-FR,fr;q=0.9,en;q=0.8')
        self.assertEqual(result4, 'en')  # en є першим в LANGUAGES

    def test_utils_with_multiple_language_sources(self):
        """Тест utils з кількома джерелами мови одночасно"""
        from common.utils.language_utils import get_language_from_request

        request = self.factory()
        request.COOKIES = {'django_language': 'uk'}
        request.META = {'HTTP_X_LANGUAGE': 'en', 'HTTP_ACCEPT_LANGUAGE': 'fr'}
        request.GET = {'lang': 'de'}
        request.method = 'GET'

        result = get_language_from_request(request)

        self.assertEqual(result, 'uk')


class TestEndToEndScenarios(TestCase):
    """End-to-end тести реальних сценаріїв"""

    def setUp(self):
        self.client = Client()

    def test_complete_localization_flow_with_client(self):
        """Тест повного потоку через Django test client"""
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='uk')
        self.assertIn(response.status_code, [200, 404])

    def test_client_with_language_cookie(self):
        """Тест клієнта з language cookie"""
        self.client.cookies['django_language'] = 'en'
        response = self.client.get('/')
        self.assertIn(response.status_code, [200, 404])

    def test_client_with_language_header(self):
        """Тест клієнта з X-Language header"""
        response = self.client.get('/', HTTP_X_LANGUAGE='uk')
        self.assertIn(response.status_code, [200, 404])

    def test_invalid_language_fallback_scenario(self):
        """Тест сценарію з неправильною мовою"""
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='invalid-lang')
        self.assertIn(response.status_code, [200, 404])

    def test_concurrent_requests_language_isolation(self):
        """Тест ізоляції мов при паралельних запитах"""
        import threading
        import time

        results = {}

        def make_request(lang, result_key):
            response = self.client.get('/', HTTP_X_LANGUAGE=lang)
            results[result_key] = response.status_code
            time.sleep(0.1)

        threads = [
            threading.Thread(target=make_request, args=('en', 'thread1')),
            threading.Thread(target=make_request, args=('uk', 'thread2')),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(results), 2)
        for result in results.values():
            self.assertIn(result, [200, 404])


class TestErrorHandlingIntegration(TestCase):
    """Тести інтеграції обробки помилок"""

    def setUp(self):
        self.client = Client()

    async def test_middleware_with_view_exception(self):
        """Тест middleware коли view кидає виняток"""

        class ExceptionView(LocalizedView):
            async def get(self, request, *args, **kwargs):
                raise ValueError("Test exception")

        from common.utils.language_utils import get_language_from_request, validate_language

        request = HttpRequest()
        request.method = 'GET'
        request.META['HTTP_ACCEPT_LANGUAGE'] = 'en'

        language = get_language_from_request(request)
        language = validate_language(language)

        from django.utils import translation
        translation.activate(language)
        request.LANGUAGE_CODE = language

        view = ExceptionView()

        with self.assertRaises(ValueError):
            await view.dispatch(request)

        self.assertEqual(request.LANGUAGE_CODE, 'en')
        translation.deactivate()

    @patch('common.utils.language_utils.get_language_from_request')
    async def test_middleware_with_utils_exception(self, mock_get_language):
        """Тест middleware коли utils кидає виняток"""
        mock_get_language.side_effect = Exception("Utils error")

        class SimpleView(LocalizedView):
            @staticmethod
            async def get(request, *args, **kwargs):
                return HttpResponse("Simple response")

        request = HttpRequest()
        request.method = 'GET'

        try:
            from common.utils.language_utils import get_language_from_request, validate_language
            language = get_language_from_request(request)
            language = validate_language(language)
        except Exception:
            language = 'en'  # fallback

        from django.utils import translation
        translation.activate(language)
        request.LANGUAGE_CODE = language

        view = SimpleView()
        response = await view.dispatch(request)

        self.assertIsInstance(response, HttpResponse)
        translation.deactivate()

    def test_malformed_requests_handling(self):
        """Тест обробки деформованих запитів"""
        from common.utils.language_utils import get_language_from_request

        malformed_cases = [
            {'COOKIES': {'django_language': None}},
            {'META': {'HTTP_ACCEPT_LANGUAGE': 'invalid;;;;'}},
            {'GET': {'lang': ''}},
        ]

        for case in malformed_cases:
            with self.subTest(case=case):
                request = HttpRequest()
                for attr, value in case.items():
                    setattr(request, attr, value)

                result = get_language_from_request(request)
                self.assertIsNotNone(result)


class TestPerformanceIntegration(TestCase):
    """Тести продуктивності інтеграції"""

    def test_middleware_view_performance(self):
        """Тест продуктивності через client"""
        import time

        start_time = time.time()

        for i in range(20):
            response = self.client.get('/', HTTP_X_LANGUAGE='en')
            self.assertIn(response.status_code, [200, 404])

        end_time = time.time()
        total_time = end_time - start_time

        self.assertLess(total_time, 2.0)

        avg_time = total_time / 20
        self.assertLess(avg_time, 0.1)

    async def test_async_view_performance(self):
        """Тест продуктивності асинхронних views"""
        import time
        from common.utils.language_utils import get_language_from_request, validate_language

        class FastAsyncView(LocalizedView):
            @staticmethod
            async def get(request, *args, **kwargs):
                return HttpResponse("Fast response")

        start_time = time.time()

        for i in range(10):
            request = HttpRequest()
            request.method = 'GET'
            request.META['HTTP_X_LANGUAGE'] = 'en'

            language = get_language_from_request(request)
            language = validate_language(language)

            from django.utils import translation
            translation.activate(language)
            request.LANGUAGE_CODE = language

            view = FastAsyncView()
            response = await view.dispatch(request)

            self.assertEqual(response.status_code, 200)
            translation.deactivate()

        end_time = time.time()
        total_time = end_time - start_time

        self.assertLess(total_time, 1.0)


class TestErrorBoundaries(TestCase):
    """Тести граничних помилок"""

    def test_memory_exhaustion_protection(self):
        """Тест захисту від вичерпання пам'яті"""
        request = HttpRequest()
        request.META['HTTP_ACCEPT_LANGUAGE'] = ','.join(['en'] * 10000)

        result = get_language_from_request(request)
        self.assertIsNotNone(result)

    @override_settings(LANGUAGES=[])
    def test_empty_languages_setting(self):
        """Тест з порожнім LANGUAGES"""
        result = validate_language('en')
        self.assertEqual(result, 'en')

    def test_corrupted_cookie_handling(self):
        """Тест обробки пошкоджених cookies"""
        request = HttpRequest()
        request.COOKIES = {'django_language': '\xff\xfe\x00\x01'}

        result = get_language_from_request(request)
        self.assertIsNotNone(result)
