from unittest.mock import patch
from django.test import TestCase
from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response

from common.views import LocalizedView, LocalizedAPIView


class TestLocalizedView(TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'GET'

    @patch.object(LocalizedView, 'async_dispatch')
    async def test_dispatch_calls_async_dispatch(self, mock_async_dispatch):
        """Тест що dispatch викликає async_dispatch з правильними аргументами"""
        mock_response = HttpResponse("Test response")
        mock_async_dispatch.return_value = mock_response

        view = LocalizedView()
        response = await view.dispatch(self.request, 'arg1', 'arg2', kwarg1='value1')

        mock_async_dispatch.assert_called_once_with(
            self.request, 'arg1', 'arg2', kwarg1='value1'
        )
        self.assertEqual(response, mock_response)

    @patch.object(LocalizedView, 'async_dispatch')
    async def test_dispatch_without_args(self, mock_async_dispatch):
        """Тест dispatch без додаткових аргументів"""
        mock_response = HttpResponse("Simple response")
        mock_async_dispatch.return_value = mock_response

        view = LocalizedView()
        response = await view.dispatch(self.request)

        mock_async_dispatch.assert_called_once_with(self.request)
        self.assertEqual(response, mock_response)

    @patch.object(LocalizedView, 'async_dispatch')
    async def test_dispatch_exception_propagation(self, mock_async_dispatch):
        """Тест що винятки з async_dispatch передаються далі"""
        mock_async_dispatch.side_effect = ValueError("Test exception")

        view = LocalizedView()

        with self.assertRaises(ValueError) as context:
            await view.dispatch(self.request)

        self.assertEqual(str(context.exception), "Test exception")
        mock_async_dispatch.assert_called_once_with(self.request)

    async def test_dispatch_is_coroutine(self):
        """Тест що dispatch є асинхронною функцією"""
        view = LocalizedView()

        import asyncio
        self.assertTrue(asyncio.iscoroutinefunction(view.dispatch))

    @patch('common.mixins.get_language_from_request')
    @patch('common.mixins.validate_language')
    @patch('django.utils.translation.activate')
    @patch('django.utils.translation.deactivate')
    async def test_dispatch_integration_with_localization(self, mock_deactivate,
                                                          mock_activate, mock_validate,
                                                          mock_get_language):
        """Тест інтеграції з локалізацією через async_dispatch"""
        mock_get_language.return_value = 'uk'
        mock_validate.return_value = 'uk'

        class TestLocalizedView(LocalizedView):
            @staticmethod
            async def get(request, *args, **kwargs):
                return HttpResponse("Ukrainian response")

        view = TestLocalizedView()
        response = await view.dispatch(self.request)

        mock_get_language.assert_called_once_with(self.request)
        mock_validate.assert_called_once_with('uk')
        mock_activate.assert_called_once_with('uk')
        mock_deactivate.assert_called_once()
        self.assertIsInstance(response, HttpResponse)


class TestLocalizedAPIView(TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'GET'

    @patch.object(LocalizedAPIView, 'async_dispatch')
    async def test_dispatch_calls_async_dispatch(self, mock_async_dispatch):
        """Тест що dispatch викликає async_dispatch з правильними аргументами"""
        mock_response = Response({"message": "Test response"})
        mock_async_dispatch.return_value = mock_response

        view = LocalizedAPIView()
        response = await view.dispatch(self.request, 'arg1', 'arg2', kwarg1='value1')

        mock_async_dispatch.assert_called_once_with(
            self.request, 'arg1', 'arg2', kwarg1='value1'
        )
        self.assertEqual(response, mock_response)

    @patch.object(LocalizedAPIView, 'async_dispatch')
    async def test_dispatch_with_drf_response(self, mock_async_dispatch):
        """Тест dispatch з DRF Response"""
        mock_response = Response({"data": "test", "status": "success"})
        mock_async_dispatch.return_value = mock_response

        view = LocalizedAPIView()
        response = await view.dispatch(self.request)

        mock_async_dispatch.assert_called_once_with(self.request)
        self.assertEqual(response, mock_response)
        self.assertEqual(response.data["data"], "test")

    @patch.object(LocalizedAPIView, 'async_dispatch')
    async def test_dispatch_exception_handling(self, mock_async_dispatch):
        """Тест обробки винятків в dispatch"""
        from rest_framework.exceptions import ValidationError
        mock_async_dispatch.side_effect = ValidationError("Invalid data")

        view = LocalizedAPIView()

        with self.assertRaises(ValidationError) as context:
            await view.dispatch(self.request)

        self.assertEqual(str(context.exception.detail[0]), "Invalid data")

    async def test_dispatch_is_coroutine(self):
        """Тест що dispatch є асинхронною функцією"""
        view = LocalizedAPIView()

        import asyncio
        self.assertTrue(asyncio.iscoroutinefunction(view.dispatch))

    @patch('common.mixins.get_language_from_request')
    @patch('common.mixins.validate_language')
    @patch('django.utils.translation.activate')
    @patch('django.utils.translation.deactivate')
    async def test_api_dispatch_with_localization(self, mock_deactivate,
                                                  mock_activate, mock_validate,
                                                  mock_get_language):
        """Тест інтеграції APIView з локалізацією"""
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        class TestLocalizedAPIView(LocalizedAPIView):
            @staticmethod
            async def get(request, *args, **kwargs):
                return Response({"message": "English API response"})

        view = TestLocalizedAPIView()
        response = await view.dispatch(self.request)

        mock_get_language.assert_called_once_with(self.request)
        mock_activate.assert_called_once_with('en')
        mock_deactivate.assert_called_once()
        self.assertIsInstance(response, Response)
        self.assertEqual(response.data["message"], "English API response")

    @patch.object(LocalizedAPIView, 'async_dispatch')
    async def test_dispatch_with_multiple_args_kwargs(self, mock_async_dispatch):
        """Тест dispatch з множинними аргументами та kwargs"""
        mock_response = Response({"processed": True})
        mock_async_dispatch.return_value = mock_response

        view = LocalizedAPIView()
        response = await view.dispatch(
            self.request,
            'arg1', 'arg2', 'arg3',
            kwarg1='value1',
            kwarg2='value2',
            kwarg3={'nested': 'value'}
        )

        mock_async_dispatch.assert_called_once_with(
            self.request,
            'arg1', 'arg2', 'arg3',
            kwarg1='value1',
            kwarg2='value2',
            kwarg3={'nested': 'value'}
        )
        self.assertEqual(response, mock_response)

    @patch('common.mixins.get_language_from_request')
    @patch('common.mixins.validate_language')
    @patch('django.utils.translation.activate')
    @patch('django.utils.translation.deactivate')
    async def test_multiple_language_requests(self, mock_deactivate,
                                              mock_activate, mock_validate,
                                              mock_get_language):
        """Тест послідовних запитів з різними мовами"""

        class TestAPIView(LocalizedAPIView):
            @staticmethod
            async def get(request, *args, **kwargs):
                return Response({"method": "get"})

        view = TestAPIView()

        # Перший запит українською
        mock_get_language.return_value = 'uk'
        mock_validate.return_value = 'uk'

        await view.dispatch(self.request)

        # Другий запит англійською
        request2 = HttpRequest()
        request2.method = 'GET'
        mock_get_language.return_value = 'en'
        mock_validate.return_value = 'en'

        await view.dispatch(request2)

        # Перевіряємо що активація відбулася для обох мов
        mock_activate.assert_any_call('uk')
        mock_activate.assert_any_call('en')
        self.assertEqual(mock_deactivate.call_count, 2)


class TestBothViews(TestCase):
    """Порівняльні тести для обох views"""
    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'GET'

    async def test_both_views_inherit_from_localized_mixin(self):
        """Тест що обидва views наслідуються від LocalizedMixin"""
        from common.mixins import LocalizedMixin

        view1 = LocalizedView()
        view2 = LocalizedAPIView()

        self.assertIsInstance(view1, LocalizedMixin)
        self.assertIsInstance(view2, LocalizedMixin)

    async def test_both_views_have_async_dispatch_method(self):
        """Тест що обидва views мають async_dispatch метод"""
        view1 = LocalizedView()
        view2 = LocalizedAPIView()

        self.assertTrue(hasattr(view1, 'async_dispatch'))
        self.assertTrue(hasattr(view2, 'async_dispatch'))

        import asyncio
        self.assertTrue(asyncio.iscoroutinefunction(view1.async_dispatch))
        self.assertTrue(asyncio.iscoroutinefunction(view2.async_dispatch))

    async def test_both_views_override_dispatch(self):
        """Тест що обидва views перевизначають dispatch метод"""
        import asyncio

        view1 = LocalizedView()
        view2 = LocalizedAPIView()

        self.assertTrue(asyncio.iscoroutinefunction(view1.dispatch))
        self.assertTrue(asyncio.iscoroutinefunction(view2.dispatch))

    @patch('common.mixins.get_language_from_request')
    @patch('common.mixins.validate_language')
    @patch('django.utils.translation.activate')
    @patch('django.utils.translation.deactivate')
    async def test_both_views_localization_behavior(self, mock_deactivate,
                                                    mock_activate, mock_validate,
                                                    mock_get_language):
        """Тест що обидва views поводяться однаково з локалізацією"""
        mock_get_language.return_value = 'fr'
        mock_validate.return_value = 'fr'

        class TestView(LocalizedView):
            @staticmethod
            async def get(request, *args, **kwargs):
                return HttpResponse("View response")

        class TestAPIView(LocalizedAPIView):
            @staticmethod
            async def get(request, *args, **kwargs):
                return Response({"message": "API response"})

        view1 = TestView()
        view2 = TestAPIView()

        # Тестуємо LocalizedView
        await view1.dispatch(self.request)

        # Тестуємо LocalizedAPIView
        request2 = HttpRequest()
        request2.method = 'GET'
        await view2.dispatch(request2)

        # Обидва повинні активувати французьку мову
        mock_activate.assert_any_call('fr')
        self.assertEqual(mock_activate.call_count, 2)
        self.assertEqual(mock_deactivate.call_count, 2)

    @patch.object(LocalizedView, 'async_dispatch')
    @patch.object(LocalizedAPIView, 'async_dispatch')
    async def test_both_views_dispatch_delegation(self, mock_api_async, mock_view_async):
        """Тест що обидва views правильно делегують до async_dispatch"""
        mock_view_async.return_value = HttpResponse("View")
        mock_api_async.return_value = Response({"api": True})

        view1 = LocalizedView()
        view2 = LocalizedAPIView()

        await view1.dispatch(self.request, 'arg1', test='value')
        await view2.dispatch(self.request, 'arg2', test='value2')

        mock_view_async.assert_called_once_with(self.request, 'arg1', test='value')
        mock_api_async.assert_called_once_with(self.request, 'arg2', test='value2')
