# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/main/LICENSE

# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring

from datetime import date, datetime, timezone
from decimal import Decimal
import unittest
from uuid import UUID

from schema_markdown import JSONEncoder, decode_query_string, encode_query_string


class TestJSONEncoder(unittest.TestCase):

    def test_types(self):
        encoder = JSONEncoder(indent=2, sort_keys=True, separators=(',', ': '))
        content = encoder.encode({
            'date': date(2016, 7, 1),
            'datetime': datetime(2016, 7, 1, 7, 56, tzinfo=timezone.utc),
            'decimal': Decimal('7.57'),
            'uuid': UUID('127FF2EB-3E1E-42A6-AB8A-F03B6EEB33E7')
        })
        self.assertEqual(content, '''\
{
  "date": "2016-07-01",
  "datetime": "2016-07-01T07:56:00+00:00",
  "decimal": 7.57,
  "uuid": "127ff2eb-3e1e-42a6-ab8a-f03b6eeb33e7"
}''')

    def test_types_no_tz(self):
        encoder = JSONEncoder(indent=2, sort_keys=True, separators=(',', ': '))
        content = encoder.encode({
            'date': date(2016, 7, 1),
            'datetime': datetime(2016, 7, 1, 7, 56),
            'decimal': Decimal('7.57'),
            'uuid': UUID('127FF2EB-3E1E-42A6-AB8A-F03B6EEB33E7')
        })
        self.assertEqual(content, '''\
{
  "date": "2016-07-01",
  "datetime": "2016-07-01T07:56:00+00:00",
  "decimal": 7.57,
  "uuid": "127ff2eb-3e1e-42a6-ab8a-f03b6eeb33e7"
}''')

    def test_types_unknown(self):
        class MyType:
            pass
        encoder = JSONEncoder(indent=2, sort_keys=True, separators=(',', ': '))
        with self.assertRaises(TypeError):
            encoder.encode({'my_type': MyType()})


class TestDecodeQueryString(unittest.TestCase):

    def test_decode_query_string(self):
        self.assertEqual(
            decode_query_string('_a=7&a=7&b.c=%2Bx%20y%20%2B%20z&b.d.0=2&b.d.1=-4&b.d.2=6'),
            {'a': '7', '_a': '7', 'b': {'c': '+x y + z', 'd': ['2', '-4', '6']}}
        )

    def test_array_of_dict(self):
        self.assertEqual(
            decode_query_string('foo.0.bar=17&foo.0.thud=blue&foo.1.boo=bear'),
            {'foo': [{'bar': '17', 'thud': 'blue'}, {'boo': 'bear'}]}
        )

    def test_array(self):
        self.assertEqual(
            decode_query_string('0=1&1=2&2=3'),
            ['1', '2', '3']
        )

    def test_empty_string(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('')
        self.assertEqual(str(cm_exc.exception), "Invalid key/value pair ''")

    def test_empty_string_value(self):
        self.assertEqual(
            decode_query_string('b='),
            {'b': ''}
        )

    def test_empty_string_value_at_end(self):
        self.assertEqual(
            decode_query_string('a=7&b='),
            {'a': '7', 'b': ''}
        )

    def test_empty_string_value_at_start(self):
        self.assertEqual(
            decode_query_string('b=&a=7'),
            {'a': '7', 'b': ''}
        )

    def test_empty_string_value_in_middle(self):
        self.assertEqual(
            decode_query_string('a=7&b=&c=9'),
            {'a': '7', 'b': '', 'c': '9'}
        )

    def test_decode_keys_and_values(self):
        self.assertEqual(
            decode_query_string('a%2eb.c=7%20+%207%20%3d%2014'),
            {'a.b': {'c': '7 + 7 = 14'}}
        )

    def test_decode_unicode_string(self):
        self.assertEqual(
            decode_query_string('a=abc%EA%80%80&b.0=c&b.1=d'),
            {'a': 'abc' + chr(40960), 'b': ['c', 'd']}
        )

    def test_key_values_special_characters(self):
        self.assertEqual(
            decode_query_string('a%26b%3Dc%2ed=a%26b%3Dc.d'),
            {'a&b=c.d': 'a&b=c.d'}
        )

    def test_array_initial_non_zero(self):
        self.assertEqual(
            decode_query_string('a.1=0'),
            {'a': {'1': '0'}}
        )

    def test_dictionary_first_then_array_looking_zero_index(self):
        self.assertEqual(
            decode_query_string('a.b=0&a.0=0'),
            {'a': {'b': '0', '0': '0'}}
        )

    def test_empty_string_key(self):
        self.assertEqual(
            decode_query_string('a=7&=b'),
            {'a': '7', '': 'b'}
        )

    def test_empty_string_key_and_value(self):
        self.assertEqual(
            decode_query_string('a=7&='),
            {'a': '7', '': ''}
        )

    def test_empty_string_key_and_value_with_space(self):
        self.assertEqual(
            decode_query_string('a=7& = '),
            {'a': '7', ' ': ' '}
        )

    def test_empty_string_key_with_no_equal(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a=7&')
        self.assertEqual(str(cm_exc.exception), "Invalid key/value pair ''")

    def test_two_empty_key_values(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('&')
        self.assertEqual(str(cm_exc.exception), "Invalid key/value pair ''")

    def test_multiple_empty_key_values(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('&&')
        self.assertEqual(str(cm_exc.exception), "Invalid key/value pair ''")

    def test_empty_string_subkey(self):
        self.assertEqual(
            decode_query_string('a.=5'),
            {'a': {'': '5'}}
        )

    def test_key_with_no_equal(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a=7&b')
        self.assertEqual(str(cm_exc.exception), "Invalid key/value pair 'b'")

    def test_key_with_no_equal_long(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a=7&' + 'b' * 2000)
        self.assertEqual(str(cm_exc.exception), f"Invalid key/value pair '{'b' * 99}")

    def test_two_empty_keys_with_no_equal(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a&b')
        self.assertEqual(str(cm_exc.exception), "Invalid key/value pair 'a'")

    def test_multiple_empty_keys_with_no_equal(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a&b&c')
        self.assertEqual(str(cm_exc.exception), "Invalid key/value pair 'a'")

    def test_duplicate_keys(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('abc=21&ab=19&abc=17')
        self.assertEqual(str(cm_exc.exception), "Duplicate key 'abc'")

    def test_duplicate_keys_long(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a' * 2000 + '=21&ab=19&' + 'a' * 2000 + '=17')
        self.assertEqual(str(cm_exc.exception), f"Duplicate key '{'a' * 99}")

    def test_duplicate_index(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a.0=0&a.1=1&a.0=2')
        self.assertEqual(str(cm_exc.exception), "Duplicate key 'a.0'")

    def test_index_too_large(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a.0=0&a.1=1&a.3=3')
        self.assertEqual(str(cm_exc.exception), "Invalid array index 3 in key 'a.3'")

    def test_index_too_large_long(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a' * 2000 + '.0=0&' + 'a' * 2000 + '.1=1&' + 'a' * 2000 + '.3=3')
        self.assertEqual(str(cm_exc.exception), f"Invalid array index 3 in key '{'a' * 99}")

    def test_negative_index(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a.0=0&a.1=1&a.-3=3')
        self.assertEqual(str(cm_exc.exception), "Invalid array index -3 in key 'a.-3'")

    def test_invalid_index(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a.0=0&a.1asdf=1')
        self.assertEqual(str(cm_exc.exception), "Invalid array index '1asdf' in key 'a.1asdf'")

    def test_first_list_then_dict(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a.0=0&a.b=0')
        self.assertEqual(str(cm_exc.exception), "Invalid array index 'b' in key 'a.b'")

    def test_first_list_then_dict_long(self):
        with self.assertRaises(ValueError) as cm_exc:
            decode_query_string('a' * 2000 + '.0=0&' + 'a' * 2000 + '.b=0')
        self.assertEqual(str(cm_exc.exception), f"Invalid array index 'b' in key '{'a' * 99}")


class TestEncodeQueryString(unittest.TestCase):

    def test_complex_dict(self):
        self.assertEqual(
            encode_query_string({'a': 7, '_a': '7', 'b': {'c': '+x y + z', 'd': [2, -4, 6]}}),
            '_a=7&a=7&b.c=%2Bx%20y%20%2B%20z&b.d.0=2&b.d.1=-4&b.d.2=6'
        )

    def test_array_of_dict(self):
        self.assertEqual(
            encode_query_string({'foo': [{'bar': '17', 'thud': 'blue'}, {'boo': 'bear'}]}),
            'foo.0.bar=17&foo.0.thud=blue&foo.1.boo=bear'
        )

    def test_array(self):
        self.assertEqual(
            encode_query_string([1, 2, 3]),
            '0=1&1=2&2=3'
        )

    def test_empty_dict(self):
        self.assertEqual(
            encode_query_string({}),
            ''
        )

    def test_empty_array(self):
        self.assertEqual(
            encode_query_string([]),
            ''
        )

    def test_empty_dict_dict(self):
        self.assertEqual(
            encode_query_string({'foo': {}}),
            'foo='
        )

    def test_empty_dict_array(self):
        self.assertEqual(
            encode_query_string({'foo': []}),
            'foo='
        )

    def test_empty_array_array(self):
        self.assertEqual(
            encode_query_string([[]]),
            '0='
        )

    def test_empty_array_dict(self):
        self.assertEqual(
            encode_query_string([{}]),
            '0='
        )

    def test_key_values_special_characters(self):
        self.assertEqual(
            encode_query_string({'a&b=c.d': 'a&b=c.d'}),
            'a%26b%3Dc.d=a%26b%3Dc.d'
        )

    def test_unicode_key_values(self):
        self.assertEqual(
            encode_query_string({'a': 'abc' + chr(40960), 'b': ['c', 'd']}),
            'a=abc%EA%80%80&b.0=c&b.1=d'
        )

    def test_null(self):
        self.assertEqual(encode_query_string(None), 'null')
        self.assertEqual(encode_query_string({'a': None, 'b': 'abc'}), 'a=null&b=abc')

    def test_non_container(self):
        self.assertEqual(encode_query_string(7), '7')
        self.assertEqual(encode_query_string('abc'), 'abc')

    def test_float(self):
        self.assertEqual(
            encode_query_string({'a': 3.14}),
            'a=3.14'
        )

    def test_bool(self):
        self.assertEqual(
            encode_query_string({'a': True}),
            'a=true'
        )

    def test_date(self):
        self.assertEqual(
            encode_query_string({'a': date(2013, 7, 18)}),
            'a=2013-07-18'
        )

    def test_datetime(self):
        self.assertEqual(
            encode_query_string({'a': datetime(2013, 7, 18, 12, 31, tzinfo=timezone.utc)}),
            'a=2013-07-18T12%3A31%3A00%2B00%3A00'
        )

    def test_datetime_naive(self):
        self.assertEqual(
            encode_query_string({'a': datetime(2013, 7, 18, 12, 31)}),
            'a=2013-07-18T12%3A31%3A00%2B00%3A00'
        )

    def test_uuid(self):
        self.assertEqual(
            encode_query_string({'a': UUID('7da81f83-a656-42f1-aeb3-ab207809fb0e')}),
            'a=7da81f83-a656-42f1-aeb3-ab207809fb0e'
        )
