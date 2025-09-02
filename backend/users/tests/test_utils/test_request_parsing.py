import json
from unittest.mock import patch, Mock

from django.test import TestCase, RequestFactory

from users.utils.request_parsing import parse_request_data


class TestRequestParsing(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_parse_request_data_multipart_form_data(self):
        """Тест парсингу multipart/form-data запиту"""
        request = Mock()
        request.content_type = 'multipart/form-data; boundary=something'
        mock_post = Mock()
        mock_post.dict.return_value = {'key': 'value'}
        request.POST = mock_post

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, {'key': 'value'})
        self.assertTrue(is_multipart)

    def test_parse_request_data_multipart_form_data_multiple_values(self):
        """Тест парсингу multipart/form-data з кількома значеннями"""
        request = Mock()
        request.content_type = 'multipart/form-data'
        mock_post = Mock()
        mock_post.dict.return_value = {'key1': 'value1', 'key2': 'value2'}
        request.POST = mock_post

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, {'key1': 'value1', 'key2': 'value2'})
        self.assertTrue(is_multipart)

    def test_parse_request_data_json_content(self):
        """Тест парсингу JSON запиту"""
        json_data = {'key': 'value', 'number': 123}
        request = self.factory.post('/',
                                    data=json.dumps(json_data),
                                    content_type='application/json')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, json_data)
        self.assertFalse(is_multipart)

    def test_parse_request_data_json_complex_data(self):
        """Тест парсингу складних JSON даних"""
        json_data = {
            'user': {'name': 'John', 'age': 30},
            'items': [1, 2, 3],
            'active': True,
            'score': 99.5
        }
        request = self.factory.post('/',
                                    data=json.dumps(json_data),
                                    content_type='application/json')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, json_data)
        self.assertFalse(is_multipart)

    def test_parse_request_data_no_content_type(self):
        """Тест парсингу запиту без content_type"""
        json_data = {'key': 'value'}
        request = Mock()
        request.content_type = None
        request.body = json.dumps(json_data).encode('utf-8')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, json_data)
        self.assertFalse(is_multipart)

    def test_parse_request_data_empty_content_type(self):
        """Тест парсингу запиту з порожнім content_type"""
        json_data = {'key': 'value'}
        request = Mock()
        request.content_type = ''
        request.body = json.dumps(json_data).encode('utf-8')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, json_data)
        self.assertFalse(is_multipart)

    def test_parse_request_data_other_content_type(self):
        """Тест парсингу запиту з іншим content_type"""
        json_data = {'key': 'value'}
        request = self.factory.post('/',
                                    data=json.dumps(json_data),
                                    content_type='application/xml')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, json_data)
        self.assertFalse(is_multipart)

    def test_parse_request_data_multipart_startswith_check(self):
        """Тест що перевіряє startswith для multipart"""
        request = Mock()
        request.content_type = 'multipart/form-data; charset=utf-8'
        mock_post = Mock()
        mock_post.dict.return_value = {'key': 'value'}
        request.POST = mock_post

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, {'key': 'value'})
        self.assertTrue(is_multipart)

    def test_parse_request_data_not_multipart_similar_name(self):
        """Тест з content_type схожим на multipart але не multipart"""
        json_data = {'key': 'value'}
        request = self.factory.post('/',
                                    data=json.dumps(json_data),
                                    content_type='application/multipart-related')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, json_data)
        self.assertFalse(is_multipart)

    def test_parse_request_data_empty_post_data(self):
        """Тест з порожніми POST даними"""
        request = self.factory.post('/')
        request.content_type = 'multipart/form-data'

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, {})
        self.assertTrue(is_multipart)

    def test_parse_request_data_empty_json_body(self):
        """Тест з порожнім JSON тілом"""
        request = self.factory.post('/', data='{}', content_type='application/json')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, {})
        self.assertFalse(is_multipart)

    @patch('users.utils.request_parsing.json.loads')
    def test_parse_request_data_json_loads_called(self, mock_json_loads):
        """Тест що json.loads викликається для не-multipart запитів"""
        mock_json_loads.return_value = {'parsed': 'data'}

        request = Mock()
        request.content_type = 'application/json'
        request.body = b'{"test": "data"}'

        data, is_multipart = parse_request_data(request)

        mock_json_loads.assert_called_once_with(request.body)
        self.assertEqual(data, {'parsed': 'data'})
        self.assertFalse(is_multipart)

    def test_parse_request_data_post_dict_called(self):
        """Тест що POST.dict() викликається для multipart запитів"""
        request = self.factory.post('/', data={'test': 'value'})
        request.content_type = 'multipart/form-data'

        with patch.object(request.POST, 'dict') as mock_dict:
            mock_dict.return_value = {'mocked': 'data'}

            data, is_multipart = parse_request_data(request)

            mock_dict.assert_called_once()
            self.assertEqual(data, {'mocked': 'data'})
            self.assertTrue(is_multipart)

    def test_parse_request_data_json_decode_error_handling(self):
        """Тест обробки помилки декодування JSON"""
        request = self.factory.post('/', data='invalid json', content_type='application/json')

        with self.assertRaises(json.JSONDecodeError):
            parse_request_data(request)

    def test_parse_request_data_return_tuple_structure(self):
        """Тест структури повернення кортежу"""
        request_multipart = Mock()
        request_multipart.content_type = 'multipart/form-data'
        mock_post = Mock()
        mock_post.dict.return_value = {'key': 'value'}
        request_multipart.POST = mock_post

        result_multipart = parse_request_data(request_multipart)
        self.assertIsInstance(result_multipart, tuple)
        self.assertEqual(len(result_multipart), 2)
        self.assertIsInstance(result_multipart[0], dict)
        self.assertIsInstance(result_multipart[1], bool)

        request_json = self.factory.post('/', data='{"key": "value"}', content_type='application/json')

        result_json = parse_request_data(request_json)
        self.assertIsInstance(result_json, tuple)
        self.assertEqual(len(result_json), 2)
        self.assertIsInstance(result_json[0], dict)
        self.assertIsInstance(result_json[1], bool)

    def test_parse_request_data_content_type_case_sensitivity(self):
        """Тест чутливості до регістру в content_type"""
        request = Mock()
        request.content_type = 'MULTIPART/FORM-DATA'
        request.body = b'{"key": "value"}'

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, {'key': 'value'})
        self.assertFalse(is_multipart)

    def test_parse_request_data_nested_json_data(self):
        """Тест з вкладеними JSON даними"""
        nested_data = {
            'level1': {
                'level2': {
                    'level3': ['a', 'b', 'c']
                }
            },
            'array': [
                {'id': 1, 'name': 'item1'},
                {'id': 2, 'name': 'item2'}
            ]
        }

        request = self.factory.post('/',
                                    data=json.dumps(nested_data),
                                    content_type='application/json')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, nested_data)
        self.assertFalse(is_multipart)

    def test_parse_request_data_multipart_with_files(self):
        """Тест multipart запиту з файлами"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        test_file = SimpleUploadedFile("test.txt", b"file content", content_type="text/plain")
        request = self.factory.post('/', data={'file': test_file, 'field': 'value'})
        request.content_type = 'multipart/form-data'

        data, is_multipart = parse_request_data(request)

        self.assertTrue(is_multipart)
        self.assertIn('field', data)
        self.assertEqual(data['field'], 'value')

    def test_parse_request_data_multipart_detection_exact_match(self):
        """Тест точного визначення multipart content type"""
        request = Mock()
        request.content_type = 'multipart/form-data'
        mock_post = Mock()
        mock_post.dict.return_value = {'key': 'value'}
        request.POST = mock_post

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, {'key': 'value'})
        self.assertTrue(is_multipart)

    def test_parse_request_data_json_with_unicode(self):
        """Тест JSON з unicode символами"""
        json_data = {'message': 'Привіт світ!', 'emoji': '🚀'}
        request = self.factory.post('/',
                                    data=json.dumps(json_data, ensure_ascii=False),
                                    content_type='application/json')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, json_data)
        self.assertFalse(is_multipart)

    def test_parse_request_data_empty_string_json(self):
        """Тест з порожнім рядком як JSON"""
        request = Mock()
        request.content_type = 'application/json'
        request.body = b''

        with self.assertRaises(json.JSONDecodeError):
            parse_request_data(request)

    def test_parse_request_data_boolean_values(self):
        """Тест з boolean значеннями в JSON"""
        json_data = {'active': True, 'disabled': False, 'null_value': None}
        request = self.factory.post('/',
                                    data=json.dumps(json_data),
                                    content_type='application/json')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, json_data)
        self.assertFalse(is_multipart)

    def test_parse_request_data_numeric_values(self):
        """Тест з числовими значеннями в JSON"""
        json_data = {'integer': 42, 'float': 3.14159, 'negative': -100}
        request = self.factory.post('/',
                                    data=json.dumps(json_data),
                                    content_type='application/json')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, json_data)
        self.assertFalse(is_multipart)

    def test_parse_request_data_large_json(self):
        """Тест обробки великих JSON файлів"""
        large_data = {'items': [{'id': i, 'name': f'item_{i}'} for i in range(1000)]}
        request = self.factory.post('/',
                                    data=json.dumps(large_data),
                                    content_type='application/json')

        data, is_multipart = parse_request_data(request)

        self.assertEqual(len(data['items']), 1000)
        self.assertFalse(is_multipart)

    def test_parse_request_data_special_characters_multipart(self):
        """Тест спеціальних символів у multipart даних"""
        request = Mock()
        request.content_type = 'multipart/form-data'
        mock_post = Mock()
        mock_post.dict.return_value = {
            'special_chars': 'äöü@#$%^&*()',
            'unicode': '🚀🌟💫'
        }
        request.POST = mock_post

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data['special_chars'], 'äöü@#$%^&*()')
        self.assertEqual(data['unicode'], '🚀🌟💫')
        self.assertTrue(is_multipart)

    def test_parse_request_data_malformed_json(self):
        """Тест некоректного JSON"""
        request = Mock()
        request.content_type = 'application/json'
        request.body = b'{"incomplete": json'

        with self.assertRaises(json.JSONDecodeError):
            parse_request_data(request)

    def test_parse_request_data_content_type_with_charset(self):
        """Тест content_type з charset"""
        request = Mock()
        request.content_type = 'multipart/form-data; charset=utf-8; boundary=----WebKitFormBoundary'
        mock_post = Mock()
        mock_post.dict.return_value = {'key': 'value'}
        request.POST = mock_post

        data, is_multipart = parse_request_data(request)

        self.assertEqual(data, {'key': 'value'})
        self.assertTrue(is_multipart)
