import asyncio
from unittest.mock import patch, AsyncMock
from django.test import TestCase
from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View

from common.mixins import LocalizedMixin


class MockView(LocalizedMixin, View):
    """Mock view для тестування синхронного dispatch"""

    @staticmethod
    def get(request, *args, **kwargs):
        return HttpResponse("Test response")


class MockAsyncView(LocalizedMixin, APIView):
    """Mock view для тестування асинхронного dispatch"""

    @staticmethod
    async def get(request, *args, **kwargs):
        return Response({"message": "async response"})

    def finalize_response(self, request, response, *args, **kwargs):
        return response


class MockSyncView(LocalizedMixin, APIView):
    """Mock view з синхронним handler для async_dispatch"""

    @staticmethod
    def get(request, *args, **kwargs):
        return Response({"message": "sync response"})

    def finalize_response(self, request, response, *args, **kwargs):
        return response


class TestLocalizedMixin(TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'GET'

    @patch('common.mixins.get_language_from_request')
    @patch('common.mixins.validate_language')
    @patch('django.utils.translation.activate')
    def test_set_language_basic(self, mock_activate, mock_validate, mock_get_language):
        """Тест основної функціональності _set_language"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        lang = LocalizedMixin._set_language(self.request)

        mock_get_language.assert_called_once_with(self.request)
        mock_validate.assert_called_once_with('en')
        mock_activate.assert_called_once_with('en')
        self.assertEqual(lang, 'en')

    @patch('common.mixins.get_language_from_request')
    @patch('common.mixins.validate_language')
    @patch('django.utils.translation.activate')
    def test_set_language_ukrainian(self, mock_activate, mock_validate, mock_get_language):
        """Тест _set_language з українською мовою"""
        mock_get_language.return_value = 'uk'
        mock_validate.return_value = 'uk'

        lang = LocalizedMixin._set_language(self.request)

        mock_activate.assert_called_once_with('uk')
        self.assertEqual(lang, 'uk')

    @patch('common.mixins.get_language_from_request')
    @patch('common.mixins.validate_language')
    @patch('django.utils.translation.activate')
    def test_set_language_validation(self, mock_activate, mock_validate, mock_get_language):
        """Тест валідації мови в _set_language"""
        mock_get_language.return_value = 'invalid'
        mock_validate.return_value = 'en'  # fallback

        lang = LocalizedMixin._set_language(self.request)

        mock_get_language.assert_called_once_with(self.request)
        mock_validate.assert_called_once_with('invalid')
        mock_activate.assert_called_once_with('en')
        self.assertEqual(lang, 'en')

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    def test_dispatch_success(self, mock_deactivate, mock_set_language):
        """Тест успішного синхронного dispatch"""
        mock_set_language.return_value = 'en'
        view = MockView()

        response = view.dispatch(self.request)

        mock_set_language.assert_called_once_with(self.request)
        mock_deactivate.assert_called_once()
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.content.decode(), "Test response")

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    def test_dispatch_exception_handling(self, mock_deactivate, mock_set_language):
        """Тест що deactivate викликається навіть при винятку в dispatch"""
        mock_set_language.return_value = 'en'

        class ExceptionView(LocalizedMixin, View):
            def get(self, request, *args, **kwargs):
                raise ValueError("Test exception")

        view = ExceptionView()

        with self.assertRaises(ValueError):
            view.dispatch(self.request)

        mock_set_language.assert_called_once_with(self.request)
        mock_deactivate.assert_called_once()

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    async def test_async_dispatch_with_async_handler(self, mock_deactivate, mock_set_language):
        """Тест async_dispatch з асинхронним handler"""
        mock_set_language.return_value = 'en'
        view = MockAsyncView()

        response = await view.async_dispatch(self.request)

        mock_set_language.assert_called_once_with(self.request)
        mock_deactivate.assert_called_once()
        self.assertIsInstance(response, Response)
        self.assertEqual(response.data["message"], "async response")
        self.assertEqual(response.request, self.request)

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    @patch('common.mixins.sync_to_async')
    async def test_async_dispatch_with_sync_handler(self, mock_sync_to_async,
                                                    mock_deactivate, mock_set_language):
        """Тест async_dispatch з синхронним handler"""
        mock_set_language.return_value = 'en'
        mock_response = Response({"message": "sync response"})
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_response)

        view = MockSyncView()
        response = await view.async_dispatch(self.request)

        mock_set_language.assert_called_once_with(self.request)
        mock_sync_to_async.assert_called_once()
        mock_deactivate.assert_called_once()
        self.assertEqual(response, mock_response)

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    @patch('common.mixins.sync_to_async')
    async def test_async_dispatch_no_handler(self, mock_sync_to_async,
                                             mock_deactivate, mock_set_language):
        """Тест async_dispatch коли handler не існує"""
        mock_set_language.return_value = 'en'
        mock_response = HttpResponse()
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_response)

        class NoHandlerView(LocalizedMixin, APIView):
            pass

        view = NoHandlerView()
        self.request.method = 'POST'  # POST handler не існує

        await view.async_dispatch(self.request)

        mock_set_language.assert_called_once_with(self.request)
        mock_sync_to_async.assert_called_once()
        mock_deactivate.assert_called_once()

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    async def test_async_dispatch_exception_handling(self, mock_deactivate, mock_set_language):
        """Тест що deactivate викликається при винятку в async_dispatch"""
        mock_set_language.return_value = 'en'

        class ExceptionAsyncView(LocalizedMixin, APIView):
            async def get(self, request, *args, **kwargs):
                raise ValueError("Async test exception")

        view = ExceptionAsyncView()

        with self.assertRaises(ValueError):
            await view.async_dispatch(self.request)

        mock_set_language.assert_called_once_with(self.request)
        mock_deactivate.assert_called_once()

    def test_asyncio_iscoroutinefunction_detection(self):
        """Тест правильного визначення асинхронних функцій"""
        view = MockAsyncView()

        # Асинхронний handler
        handler = getattr(view, 'get')
        self.assertTrue(asyncio.iscoroutinefunction(handler))

        # Синхронний handler
        sync_view = MockSyncView()
        sync_handler = getattr(sync_view, 'get')
        self.assertFalse(asyncio.iscoroutinefunction(sync_handler))

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    async def test_async_dispatch_without_finalize_response(self, mock_deactivate, mock_set_language):
        """Тест async_dispatch з view без finalize_response"""
        mock_set_language.return_value = 'en'

        class SimpleAsyncView(LocalizedMixin):
            @staticmethod
            async def get(request, *args, **kwargs):
                return Response({"message": "simple response"})

        view = SimpleAsyncView()
        response = await view.async_dispatch(self.request)

        self.assertIsInstance(response, Response)
        self.assertFalse(hasattr(response, 'request'))
        mock_deactivate.assert_called_once()

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    async def test_async_dispatch_non_response_object(self, mock_deactivate, mock_set_language):
        """Тест async_dispatch з не-Response об'єктом"""
        mock_set_language.return_value = 'en'

        class HttpResponseAsyncView(LocalizedMixin):
            @staticmethod
            async def get(request, *args, **kwargs):
                return HttpResponse("Not a DRF Response")

            @staticmethod
            def finalize_response(request, response, *args, **kwargs):
                return response

        view = HttpResponseAsyncView()
        response = await view.async_dispatch(self.request)

        self.assertIsInstance(response, HttpResponse)
        self.assertFalse(hasattr(response, 'request'))
        mock_deactivate.assert_called_once()

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    def test_dispatch_with_args_kwargs(self, mock_deactivate, mock_set_language):
        """Тест dispatch з аргументами та kwargs"""
        mock_set_language.return_value = 'en'

        class ArgsView(LocalizedMixin, View):
            @staticmethod
            def get(request, *args, **kwargs):
                return HttpResponse(f"args: {args}, kwargs: {kwargs}")

        view = ArgsView()
        response = view.dispatch(self.request, 'test_arg', test_kwarg='test_value')

        self.assertIn('test_arg', response.content.decode())
        self.assertIn('test_kwarg', response.content.decode())
        mock_deactivate.assert_called_once()

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    async def test_async_dispatch_with_args_kwargs(self, mock_deactivate, mock_set_language):
        """Тест async_dispatch з аргументами та kwargs"""
        mock_set_language.return_value = 'en'

        class AsyncArgsView(LocalizedMixin, APIView):
            @staticmethod
            async def get(request, *args, **kwargs):
                return Response({"args": list(args), "kwargs": kwargs})

            def finalize_response(self, request, response, *args, **kwargs):
                return response

        view = AsyncArgsView()
        response = await view.async_dispatch(self.request, 'test_arg', test_kwarg='test_value')

        self.assertEqual(response.data["args"], ['test_arg'])
        self.assertEqual(response.data["kwargs"], {'test_kwarg': 'test_value'})
        mock_deactivate.assert_called_once()

    @patch('common.mixins.get_language_from_request')
    @patch('common.mixins.validate_language')
    @patch('django.utils.translation.activate')
    @patch('django.utils.translation.deactivate')
    def test_multiple_requests_language_isolation(self, mock_deactivate, mock_activate,
                                                  mock_validate, mock_get_language):
        """Тест ізоляції мов між різними запитами"""
        view = MockView()

        # Перший запит з англійською
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'
        view.dispatch(self.request)

        # Другий запит з українською
        request2 = HttpRequest()
        request2.method = 'GET'
        mock_get_language.return_value = 'uk'
        mock_validate.return_value = 'uk'
        view.dispatch(request2)

        # Перевіряємо що activate викликався для обох мов
        mock_activate.assert_any_call('en')
        mock_activate.assert_any_call('uk')
        self.assertEqual(mock_deactivate.call_count, 2)

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    def test_dispatch_inheritance_chain(self, mock_deactivate, mock_set_language):
        """Тест роботи з ланцюгом наслідування"""
        mock_set_language.return_value = 'en'

        class MiddleView(View):
            @staticmethod
            def get(request, *args, **kwargs):
                return HttpResponse("Middle view response")

        class FinalView(LocalizedMixin, MiddleView):
            pass

        view = FinalView()
        response = view.dispatch(self.request)

        self.assertEqual(response.content.decode(), "Middle view response")
        mock_set_language.assert_called_once_with(self.request)
        mock_deactivate.assert_called_once()

    @patch.object(LocalizedMixin, '_set_language')
    @patch('django.utils.translation.deactivate')
    async def test_async_exception_translation_cleanup(self, mock_deactivate, mock_set_language):
        """Тест що translation очищається навіть при async винятках"""
        mock_set_language.return_value = 'en'

        class AsyncExceptionView(LocalizedMixin, APIView):
            async def get(self, request, *args, **kwargs):
                await asyncio.sleep(0.001)
                raise ValueError("Async exception")

        view = AsyncExceptionView()

        with self.assertRaises(ValueError):
            await view.async_dispatch(self.request)

        mock_deactivate.assert_called_once()
