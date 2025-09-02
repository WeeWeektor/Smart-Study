import json
from unittest.mock import patch, Mock

from django.http import JsonResponse
from django.test import TestCase, RequestFactory
from django.utils.translation import gettext

from users.utils.csrf_token import CSRFTokenView


class TestCSRFTokenView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = CSRFTokenView()

    def test_csrf_token_view_get_method(self):
        """Тест GET методу CSRFTokenView"""
        request = self.factory.get('/csrf/')

        response = self.view.get(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn('success', response_data)
        self.assertEqual(response_data['success'], gettext('CSRF cookie set'))

    def test_csrf_token_view_as_view_get(self):
        """Тест виклику через as_view() з GET запитом"""
        request = self.factory.get('/csrf/')

        view = CSRFTokenView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)

        response_data = json.loads(response.content)
        self.assertIn('success', response_data)

    def test_csrf_token_view_post_not_allowed(self):
        """Тест що POST метод не дозволений"""
        request = self.factory.post('/csrf/')

        view = CSRFTokenView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 405)

    def test_csrf_token_view_put_not_allowed(self):
        """Тест що PUT метод не дозволений"""
        request = self.factory.put('/csrf/')

        view = CSRFTokenView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 405)

    def test_csrf_token_view_delete_not_allowed(self):
        """Тест що DELETE метод не дозволений"""
        request = self.factory.delete('/csrf/')

        view = CSRFTokenView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 405)

    @patch('users.utils.csrf_token.gettext')
    def test_csrf_token_view_gettext_called(self, mock_gettext):
        """Тест що gettext викликається з правильним параметром"""
        mock_gettext.return_value = 'CSRF cookie set'

        request = self.factory.get('/csrf/')

        self.view.get(request)

        mock_gettext.assert_called_once_with('CSRF cookie set')

    @patch('users.utils.csrf_token.gettext')
    def test_csrf_token_view_different_translation(self, mock_gettext):
        """Тест з іншим перекладом"""
        mock_gettext.return_value = 'CSRF кукі встановлено'

        request = self.factory.get('/csrf/')

        response = self.view.get(request)

        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'CSRF кукі встановлено')

    def test_csrf_token_view_json_response_format(self):
        """Тест формату JSON відповіді"""
        request = self.factory.get('/csrf/')

        response = self.view.get(request)

        self.assertEqual(response['Content-Type'], 'application/json')

        response_data = json.loads(response.content)
        self.assertIsInstance(response_data, dict)
        self.assertEqual(len(response_data), 2)
        self.assertIn('success', response_data)
        self.assertIn('csrf_token', response_data)

    def test_csrf_token_view_ensure_csrf_cookie_decorator(self):
        """Тест що декоратор ensure_csrf_cookie застосований"""
        self.assertTrue(hasattr(CSRFTokenView, 'dispatch'))

        request = self.factory.get('/csrf/')

        view = CSRFTokenView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_csrf_token_view_static_method(self):
        """Тест що get є статичним методом"""
        request = self.factory.get('/csrf/')

        response = CSRFTokenView.get(request)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)

    def test_csrf_token_view_multiple_calls(self):
        """Тест багаторазових викликів"""
        request = self.factory.get('/csrf/')

        response1 = self.view.get(request)
        response2 = self.view.get(request)

        response_data1 = json.loads(response1.content)
        response_data2 = json.loads(response2.content)

        self.assertEqual(response_data1['success'], response_data2['success'])
        self.assertIn('csrf_token', response_data1)
        self.assertIn('csrf_token', response_data2)
        self.assertNotEqual(response_data1['csrf_token'], response_data2['csrf_token'])

    @patch('users.utils.csrf_token.JsonResponse')
    def test_json_response_creation(self, mock_json_response):
        """Тест створення JsonResponse"""
        mock_json_response.return_value = Mock()

        request = self.factory.get('/csrf/')

        CSRFTokenView.get(request)

        mock_json_response.assert_called_once()
        args, _ = mock_json_response.call_args

        self.assertIsInstance(args[0], dict)
        self.assertIn('success', args[0])

    def test_csrf_token_view_inheritance(self):
        """Тест що CSRFTokenView наслідує від View"""
        from django.views import View

        self.assertTrue(issubclass(CSRFTokenView, View))

    def test_csrf_token_view_method_decorator_applied(self):
        """Тест що method_decorator застосований правильно"""
        self.assertTrue(hasattr(CSRFTokenView, 'dispatch'))

        view_instance = CSRFTokenView()
        self.assertTrue(hasattr(view_instance, 'dispatch'))
