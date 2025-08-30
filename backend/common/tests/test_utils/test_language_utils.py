from django.test import TestCase, RequestFactory

from common.utils.language_utils import validate_language, parce_accept_language, get_language_from_request
from smartStudy_backend import settings


class TestGetLanguageFromRequest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_returns_language_from_django_language_cookie(self):
        request = self.factory.get('/')
        request.COOKIES['django_language'] = 'UK'
        self.assertEqual(get_language_from_request(request), 'uk')

    def test_returns_language_from_language_cookie(self):
        request = self.factory.get('/')
        request.COOKIES['language'] = 'EN'
        self.assertEqual(get_language_from_request(request), 'en')

    def test_returns_language_from_x_language_header(self):
        request = self.factory.get('/', HTTP_X_LANGUAGE='Uk')
        self.assertEqual(get_language_from_request(request), 'uk')

    def test_returns_language_from_x_request_language_header(self):
        request = self.factory.get('/', HTTP_X_REQUEST_LANGUAGE='EN')
        self.assertEqual(get_language_from_request(request), 'en')

    def test_returns_language_from_get_param(self):
        request = self.factory.get('/?lang=Uk')
        self.assertEqual(get_language_from_request(request), 'uk')

    def test_returns_language_from_post_param(self):
        request = self.factory.post('/', data={'lang': 'EN'})
        self.assertEqual(get_language_from_request(request), 'en')

    def test_returns_language_from_accept_language_header(self):
        request = self.factory.get('/', HTTP_ACCEPT_LANGUAGE='EN-us,en;q=0.9,UK;q=0.8')
        self.assertEqual(get_language_from_request(request), 'en')

    def test_returns_default_language_if_no_source(self):
        request = self.factory.get('/')
        self.assertEqual(get_language_from_request(request), settings.LANGUAGE_CODE.lower())


class ParceAcceptLanguageTestCase(TestCase):
    def test_returns_none_if_header_empty(self):
        self.assertIsNone(parce_accept_language(''))

    def test_returns_first_valid_language_from_header(self):
        header = 'fr-CH, fr;q=0.9, EN;q=0.8, de;q=0.7, *;q=0.5'
        self.assertEqual(parce_accept_language(header), 'en')

    def test_returns_none_if_no_valid_languages(self):
        header = 'fr-CH, fr;q=0.9, de;q=0.7'
        self.assertIsNone(parce_accept_language(header))

    def test_returns_uk_if_present(self):
        header = 'uk-UA, UK;q=0.9'
        self.assertEqual(parce_accept_language(header), 'uk')

    def test_returns_lowercase_code_even_if_uppercase_provided(self):
        header = 'EN-us, EN;q=0.9'
        self.assertEqual(parce_accept_language(header), 'en')

class ValidateLanguageTestCase(TestCase):
    def test_returns_default_if_language_is_none(self):
        self.assertEqual(validate_language(None), settings.LANGUAGE_CODE.lower())

    def test_returns_default_if_language_is_empty(self):
        self.assertEqual(validate_language(''), settings.LANGUAGE_CODE.lower())

    def test_returns_default_if_language_invalid(self):
        self.assertEqual(validate_language('xx'), settings.LANGUAGE_CODE.lower())

    def test_returns_same_if_language_valid_en(self):
        self.assertEqual(validate_language('EN'), 'en')

    def test_returns_same_if_language_valid_uk(self):
        self.assertEqual(validate_language('Uk'), 'uk')
