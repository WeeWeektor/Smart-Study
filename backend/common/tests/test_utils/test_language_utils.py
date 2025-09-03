from django.test import TestCase, RequestFactory

from common.utils.language_utils import validate_language, parce_accept_language, get_language_from_request, \
    _extract_language_code
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


class TestExtractLanguageCode(TestCase):
    """Тести для функції _extract_language_code"""

    def test_none_and_invalid_input(self):
        """Тест обробки None та невалідних входів"""
        self.assertIsNone(_extract_language_code(None))
        self.assertIsNone(_extract_language_code(''))
        self.assertIsNone(_extract_language_code(123))
        self.assertIsNone(_extract_language_code([]))
        self.assertIsNone(_extract_language_code({}))
        self.assertIsNone(_extract_language_code(True))

    def test_valid_simple_language_codes(self):
        """Тест валідних простих мовних кодів"""
        self.assertEqual(_extract_language_code('en'), 'en')
        self.assertEqual(_extract_language_code('uk'), 'uk')
        self.assertEqual(_extract_language_code('fr'), 'fr')
        self.assertEqual(_extract_language_code('de'), 'de')
        self.assertEqual(_extract_language_code('es'), 'es')
        self.assertEqual(_extract_language_code('ru'), 'ru')

    def test_language_codes_with_regions(self):
        """Тест мовних кодів з регіонами"""
        self.assertEqual(_extract_language_code('en-US'), 'en-US')
        self.assertEqual(_extract_language_code('en-GB'), 'en-GB')
        self.assertEqual(_extract_language_code('uk-UA'), 'uk-UA')
        self.assertEqual(_extract_language_code('fr-FR'), 'fr-FR')
        self.assertEqual(_extract_language_code('de-DE'), 'de-DE')

    def test_case_preservation(self):
        """Тест збереження регістру"""
        self.assertEqual(_extract_language_code('EN'), 'EN')
        self.assertEqual(_extract_language_code('En'), 'En')
        self.assertEqual(_extract_language_code('eN'), 'eN')
        self.assertEqual(_extract_language_code('EN-us'), 'EN-us')
        self.assertEqual(_extract_language_code('en-US'), 'en-US')

    def test_with_quality_values(self):
        """Тест з quality values (q-факторами)"""
        self.assertEqual(_extract_language_code('en;q=0.9'), 'en')
        self.assertEqual(_extract_language_code('uk;q=1.0'), 'uk')
        self.assertEqual(_extract_language_code('en-US;q=0.8'), 'en-US')
        self.assertEqual(_extract_language_code('fr-FR;q=0.7,en;q=0.5'), 'fr-FR')

    def test_with_comma_separated_languages(self):
        """Тест з комою розділеними мовами"""
        self.assertEqual(_extract_language_code('en,uk,fr'), 'en')
        self.assertEqual(_extract_language_code('uk,en'), 'uk')
        self.assertEqual(_extract_language_code('fr-FR,en-US,uk'), 'fr-FR')
        self.assertEqual(_extract_language_code(' uk , en , fr '), 'uk')

    def test_complex_accept_language_header(self):
        """Тест складних Accept-Language заголовків"""
        self.assertEqual(_extract_language_code('en-US,en;q=0.9,uk;q=0.8'), 'en-US')
        self.assertEqual(_extract_language_code('uk-UA,uk;q=0.9,en;q=0.8,*;q=0.5'), 'uk-UA')
        self.assertEqual(_extract_language_code('fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'), 'fr-FR')

    def test_with_whitespace(self):
        """Тест з пробілами"""
        self.assertEqual(_extract_language_code(' en '), 'en')
        self.assertEqual(_extract_language_code('  uk-UA  '), 'uk-UA')
        self.assertEqual(_extract_language_code('\ten\t'), 'en')
        self.assertEqual(_extract_language_code('\n uk \n'), 'uk')

    def test_malicious_input_filtering(self):
        """Тест фільтрації шкідливого вводу"""
        self.assertEqual(_extract_language_code("en'; DROP TABLE users; --"), 'en')
        self.assertEqual(_extract_language_code("uk' OR 1=1"), 'ukOR')

        self.assertIsNone(_extract_language_code('<script>alert("xss")</script>en'))
        self.assertEqual(_extract_language_code('en<img src=x>'), 'enimgsrcx')

        self.assertEqual(_extract_language_code('en@#$%^&*()'), 'en')
        self.assertEqual(_extract_language_code('uk!@#$%^&*()'), 'uk')

    def test_numeric_and_special_characters_removal(self):
        """Тест видалення цифр та спеціальних символів"""
        self.assertEqual(_extract_language_code('en123'), 'en')
        self.assertEqual(_extract_language_code('uk456'), 'uk')
        self.assertEqual(_extract_language_code('en-US123'), 'en-US')
        self.assertEqual(_extract_language_code('fr@#$FR'), 'frFR')
        self.assertEqual(_extract_language_code('de_DE'), 'deDE')
        self.assertEqual(_extract_language_code('es.ES'), 'esES')

    def test_length_restrictions(self):
        """Тест обмежень довжини"""
        long_input = 'a' * 51
        self.assertIsNone(_extract_language_code(long_input))

        valid_long_input = 'a' * 50
        self.assertIsNone(_extract_language_code(valid_long_input))

        input_with_noise = 'a1b2c3d4e5f6g7h8i9j0k'
        self.assertIsNone(_extract_language_code(input_with_noise))

        valid_cleaned = 'a1b2c3d4e5f6g7h8i9j'
        self.assertEqual(_extract_language_code(valid_cleaned), 'abcdefghij')

        short_valid = 'a1b2c3d'
        self.assertEqual(_extract_language_code(short_valid), 'abcd')

    def test_empty_result_after_cleaning(self):
        """Тест випадків, коли після очищення результат порожній"""
        self.assertIsNone(_extract_language_code('123456'))
        self.assertIsNone(_extract_language_code('!@#$%^'))
        self.assertIsNone(_extract_language_code('(){}[]'))
        self.assertIsNone(_extract_language_code('   '))
        self.assertIsNone(_extract_language_code(';;;,,,'))

    def test_only_allowed_characters(self):
        """Тест збереження тільки дозволених символів (літери та дефіс)"""
        self.assertEqual(_extract_language_code('en-US'), 'en-US')
        self.assertEqual(_extract_language_code('a-b-c-d'), 'a-b-c-d')
        self.assertEqual(_extract_language_code('ABC-def'), 'ABC-def')

        self.assertEqual(_extract_language_code('en_US'), 'enUS')
        self.assertEqual(_extract_language_code('en.US'), 'enUS')
        self.assertEqual(_extract_language_code('en/US'), 'enUS')

    def test_edge_cases_with_separators(self):
        """Тест крайових випадків з роздільниками"""
        self.assertIsNone(_extract_language_code(';'))
        self.assertIsNone(_extract_language_code(','))
        self.assertIsNone(_extract_language_code(';,;,'))

        self.assertIsNone(_extract_language_code(';en'))
        self.assertIsNone(_extract_language_code(',uk'))

        self.assertEqual(_extract_language_code('en;;;uk'), 'en')
        self.assertEqual(_extract_language_code('uk,,,en'), 'uk')

    def test_real_world_examples(self):
        """Тест реальних прикладів з браузерів"""
        # Chrome
        self.assertEqual(_extract_language_code('uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7'), 'uk-UA')

        # Firefox
        self.assertEqual(_extract_language_code('uk,en-US;q=0.7,en;q=0.3'), 'uk')

        # Safari
        self.assertEqual(_extract_language_code('en-US,en;q=0.9'), 'en-US')

        # Edge
        self.assertEqual(_extract_language_code('uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3'), 'uk-UA')

    def test_boundary_conditions(self):
        """Тест граничних умов"""
        input_50 = 'a' * 48 + ';q'
        self.assertIsNone(_extract_language_code(input_50))

        input_51 = 'a' * 49 + ';q'
        self.assertIsNone(_extract_language_code(input_51))

        input_exactly_10 = 'abcde12345fghij'
        self.assertEqual(_extract_language_code(input_exactly_10), 'abcdefghij')

        input_11 = 'abcde12345fghijk'
        self.assertIsNone(_extract_language_code(input_11))

    def test_unicode_handling(self):
        """Тест обробки Unicode символів"""
        self.assertEqual(_extract_language_code('en🇺🇸'), 'en')
        self.assertEqual(_extract_language_code('uk🇺🇦'), 'uk')
        self.assertEqual(_extract_language_code('енUA'), 'UA')
        self.assertEqual(_extract_language_code('en中文'), 'en')

    def test_maximum_allowed_length_examples(self):
        """Тест прикладів з максимально дозволеною довжиною"""
        self.assertEqual(_extract_language_code('abcdefghij'), 'abcdefghij')
        self.assertEqual(_extract_language_code('en-US-test'), 'en-US-test')

        self.assertEqual(_extract_language_code('en-US-abc'), 'en-US-abc')

        self.assertIsNone(_extract_language_code('abcdefghijk'))
        self.assertIsNone(_extract_language_code('en-US-tests'))


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


class TestEdgeCases(TestCase):
    """Граничні випадки"""

    def test_extremely_long_accept_language_header(self):
        """Тест з дуже довгим Accept-Language header"""
        long_header = ','.join([f'lang{i}-XX' for i in range(100)])
        result = parce_accept_language(long_header)
        self.assertIsNone(result)

    def test_malformed_accept_language_headers(self):
        """Тест з некоректними headers"""
        malformed = ['en;q=invalid', 'en-US;q=1.5', ';;;en;;;', 'en,,,uk,,,']
        for header in malformed:
            with self.subTest(header=header):
                result = parce_accept_language(header)
                self.assertIn(result, [None, 'en', 'uk'])

    def test_accept_language_dos_protection(self):
        """Тест захисту від DoS через Accept-Language"""
        many_langs = ','.join([f'lang{i}' for i in range(1000)])
        result = parce_accept_language(many_langs)
        self.assertIsNone(result)

    def test_accept_language_nested_parsing(self):
        """Тест складного парсингу Accept-Language"""
        complex_header = 'en-US;q=0.9;level=1,en;q=0.8;charset=utf-8,uk;q=0.7'
        result = parce_accept_language(complex_header)
        self.assertEqual(result, 'en')

    def test_accept_language_special_characters(self):
        """Тест спеціальних символів в Accept-Language"""
        special_headers = [
            'en\r\n',
            'en\t\t',
            'en;q=\x00',
            'en\xff\xfe',
        ]
        for header in special_headers:
            with self.subTest(header=header):
                result = parce_accept_language(header)
                self.assertIn(result, [None, 'en', 'uk'])
