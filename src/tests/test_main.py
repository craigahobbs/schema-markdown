# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/master/LICENSE

# pylint: disable=missing-docstring

from io import StringIO
import json
import os
import unittest.mock as unittest_mock

from schema_markdown import SchemaMarkdownParserError, ValidationError
from schema_markdown.main import main
import schema_markdown.__main__

from . import TestCase


TEST_SCHEMA_MARKDOWN = '''\
struct MyStruct
    int a
    optional bool b
'''

TEST_MODEL = '''\
{
    "title": "Index",
    "types": {
        "MyStruct": {
            "struct": {
                "members": [
                    {
                        "name": "a",
                        "type": {
                            "builtin": "int"
                        }
                    },
                    {
                        "name": "b",
                        "optional": true,
                        "type": {
                            "builtin": "bool"
                        }
                    }
                ],
                "name": "MyStruct"
            }
        }
    }
}'''

TEST_VALUE = '''\
{
    "a": "5",
    "b": "true"
}'''


class TestMain(TestCase):

    def test_package_main(self):
        self.assertTrue(schema_markdown.__main__)

    def test_compile(self):
        test_files = [
            ('test.smd', TEST_SCHEMA_MARKDOWN)
        ]
        with self.create_test_files(test_files) as input_dir:
            input_path = os.path.join(input_dir, 'test.smd')
            output_path = os.path.join(input_dir, 'test.json')
            argv = ['python3 -m schema_markdown', 'compile', input_path, '-o', output_path]
            with unittest_mock.patch('sys.stdout', new=StringIO()) as stdout, \
                 unittest_mock.patch('sys.stderr', new=StringIO()) as stderr, \
                 unittest_mock.patch('sys.argv', argv):
                main()

            self.assertEqual(stdout.getvalue(), '')
            self.assertEqual(stderr.getvalue(), '')
            with open(output_path, 'r', encoding='utf-8') as output_file:
                self.assertEqual(output_file.read(), TEST_MODEL)

    def test_compile_title(self):
        test_files = [
            ('test.smd', TEST_SCHEMA_MARKDOWN)
        ]
        with self.create_test_files(test_files) as input_dir:
            input_path = os.path.join(input_dir, 'test.smd')
            output_path = os.path.join(input_dir, 'test.json')
            argv = ['python3 -m schema_markdown', 'compile', input_path, '-o', output_path, '--title', 'My Type Model']
            with unittest_mock.patch('sys.stdout', new=StringIO()) as stdout, \
                 unittest_mock.patch('sys.stderr', new=StringIO()) as stderr, \
                 unittest_mock.patch('sys.argv', argv):
                main()

            self.assertEqual(stdout.getvalue(), '')
            self.assertEqual(stderr.getvalue(), '')
            with open(output_path, 'r', encoding='utf-8') as output_file:
                self.assertEqual(output_file.read(), TEST_MODEL.replace('"title": "Index"', '"title": "My Type Model"'))

    def test_compile_multiple(self):
        test_files = [
            ('test.smd', TEST_SCHEMA_MARKDOWN),
            ('test2.smd', 'struct MyStruct2 (MyStruct)')
        ]
        with self.create_test_files(test_files) as input_dir:
            input_path = os.path.join(input_dir, 'test.smd')
            input_path2 = os.path.join(input_dir, 'test2.smd')
            output_path = os.path.join(input_dir, 'test.json')
            argv = ['python3 -m schema_markdown', 'compile', input_path2, input_path, '-o', output_path]
            with unittest_mock.patch('sys.stdout', new=StringIO()) as stdout, \
                 unittest_mock.patch('sys.stderr', new=StringIO()) as stderr, \
                 unittest_mock.patch('sys.argv', argv):
                main()

            self.assertEqual(stdout.getvalue(), '')
            self.assertEqual(stderr.getvalue(), '')
            with open(output_path, 'r', encoding='utf-8') as output_file:
                self.assertEqual(output_file.read(), '''\
{
    "title": "Index",
    "types": {
        "MyStruct": {
            "struct": {
                "members": [
                    {
                        "name": "a",
                        "type": {
                            "builtin": "int"
                        }
                    },
                    {
                        "name": "b",
                        "optional": true,
                        "type": {
                            "builtin": "bool"
                        }
                    }
                ],
                "name": "MyStruct"
            }
        },
        "MyStruct2": {
            "struct": {
                "bases": [
                    "MyStruct"
                ],
                "name": "MyStruct2"
            }
        }
    }
}''')

    def test_compile_compact(self):
        test_files = [
            ('test.smd', TEST_SCHEMA_MARKDOWN)
        ]
        with self.create_test_files(test_files) as input_dir:
            input_path = os.path.join(input_dir, 'test.smd')
            output_path = os.path.join(input_dir, 'test.json')
            argv = ['python3 -m schema_markdown', 'compile', input_path, '-o', output_path, '--compact']
            with unittest_mock.patch('sys.stdout', new=StringIO()) as stdout, \
                 unittest_mock.patch('sys.stderr', new=StringIO()) as stderr, \
                 unittest_mock.patch('sys.argv', argv):
                main()

            self.assertEqual(stdout.getvalue(), '')
            self.assertEqual(stderr.getvalue(), '')
            with open(output_path, 'r', encoding='utf-8') as output_file:
                self.assertEqual(output_file.read(), json.dumps(json.loads(TEST_MODEL)))

    def test_compile_stdin_stdout(self):
        argv = ['python3 -m schema_markdown', 'compile']
        with unittest_mock.patch('sys.stdin', new=StringIO(TEST_SCHEMA_MARKDOWN)), \
             unittest_mock.patch('sys.stdout', new=StringIO()) as stdout, \
             unittest_mock.patch('sys.stderr', new=StringIO()) as stderr, \
             unittest_mock.patch('sys.argv', argv):
            main()

        self.assertEqual(stderr.getvalue(), '')
        self.assertEqual(stdout.getvalue(), TEST_MODEL)

    def test_compile_stdin(self):
        with self.create_test_files([]) as input_dir:
            output_path = os.path.join(input_dir, 'test.json')
            argv = ['python3 -m schema_markdown', 'compile', '-o', output_path]
            with unittest_mock.patch('sys.stdin', new=StringIO(TEST_SCHEMA_MARKDOWN)), \
                 unittest_mock.patch('sys.stdout', new=StringIO()) as stdout, \
                 unittest_mock.patch('sys.stderr', new=StringIO()) as stderr, \
                 unittest_mock.patch('sys.argv', argv):
                main()

            self.assertEqual(stderr.getvalue(), '')
            self.assertEqual(stdout.getvalue(), '')
            with open(output_path, 'r', encoding='utf-8') as output_file:
                self.assertEqual(output_file.read(), TEST_MODEL)

    def test_compile_error(self):
        argv = ['python3 -m schema_markdown', 'compile']
        with unittest_mock.patch('sys.stdin', new=StringIO('asdf')), \
             unittest_mock.patch('sys.stdout', new=StringIO()), \
             unittest_mock.patch('sys.stderr', new=StringIO()), \
             unittest_mock.patch('sys.argv', argv):
            with self.assertRaises(SchemaMarkdownParserError):
                main()

    def test_validate_schema(self):
        test_files = [
            ('test.smd', TEST_SCHEMA_MARKDOWN),
            ('value.json', TEST_VALUE)
        ]
        with self.create_test_files(test_files) as input_dir:
            input_path = os.path.join(input_dir, 'value.json')
            schema_path = os.path.join(input_dir, 'test.smd')
            argv = ['python3 -m schema_markdown', 'validate', schema_path, 'MyStruct', input_path]
            with unittest_mock.patch('sys.stdout', new=StringIO()) as stdout, \
                 unittest_mock.patch('sys.stderr', new=StringIO()) as stderr, \
                 unittest_mock.patch('sys.argv', argv):
                main()

            self.assertEqual(stdout.getvalue(), '')
            self.assertEqual(stderr.getvalue(), '')

    def test_validate_multiple(self):
        test_files = [
            ('test.smd', TEST_SCHEMA_MARKDOWN),
            ('value.json', TEST_VALUE),
            ('value2.json', TEST_VALUE)
        ]
        with self.create_test_files(test_files) as input_dir:
            schema_path = os.path.join(input_dir, 'test.smd')
            input_path = os.path.join(input_dir, 'value.json')
            input_path2 = os.path.join(input_dir, 'value2.json')
            argv = ['python3 -m schema_markdown', 'validate', schema_path, 'MyStruct', input_path, input_path2]
            with unittest_mock.patch('sys.stdout', new=StringIO()) as stdout, \
                 unittest_mock.patch('sys.stderr', new=StringIO()) as stderr, \
                 unittest_mock.patch('sys.argv', argv):
                main()

            self.assertEqual(stdout.getvalue(), '')
            self.assertEqual(stderr.getvalue(), '')

    def test_validate_error(self):
        test_files = [
            ('test.smd', TEST_SCHEMA_MARKDOWN),
            ('value.json', TEST_VALUE),
            ('value2.json', '{}')
        ]
        with self.create_test_files(test_files) as input_dir:
            input_path = os.path.join(input_dir, 'value.json')
            input_path2 = os.path.join(input_dir, 'value2.json')
            schema_path = os.path.join(input_dir, 'test.smd')
            argv = ['python3 -m schema_markdown', 'validate', schema_path, 'MyStruct', input_path, input_path2]
            with unittest_mock.patch('sys.stdout', new=StringIO()), \
                 unittest_mock.patch('sys.stderr', new=StringIO()), \
                 unittest_mock.patch('sys.argv', argv):
                with self.assertRaises(ValidationError):
                    main()

    def test_validate_schema_error(self):
        test_files = [
            ('test.smd', 'asdf'),
            ('value.json', TEST_VALUE)
        ]
        with self.create_test_files(test_files) as input_dir:
            schema_path = os.path.join(input_dir, 'test.smd')
            input_path = os.path.join(input_dir, 'value.json')
            argv = ['python3 -m schema_markdown', 'validate', schema_path, 'MyStruct', input_path]
            with unittest_mock.patch('sys.stdout', new=StringIO()), \
                 unittest_mock.patch('sys.stderr', new=StringIO()), \
                 unittest_mock.patch('sys.argv', argv):
                with self.assertRaises(SchemaMarkdownParserError):
                    main()

    def test_validate_value_error(self):
        test_files = [
            ('test.smd', TEST_SCHEMA_MARKDOWN),
            ('value.json', '{}')
        ]
        with self.create_test_files(test_files) as input_dir:
            schema_path = os.path.join(input_dir, 'test.smd')
            input_path = os.path.join(input_dir, 'value.json')
            argv = ['python3 -m schema_markdown', 'validate', schema_path, 'MyStruct', input_path]
            with unittest_mock.patch('sys.stdout', new=StringIO()), \
                 unittest_mock.patch('sys.stderr', new=StringIO()), \
                 unittest_mock.patch('sys.argv', argv):
                with self.assertRaises(ValidationError):
                    main()

    def test_validate_stdin(self):
        test_files = [
            ('test.smd', TEST_SCHEMA_MARKDOWN)
        ]
        with self.create_test_files(test_files) as input_dir:
            schema_path = os.path.join(input_dir, 'test.smd')
            argv = ['python3 -m schema_markdown', 'validate', schema_path, 'MyStruct']
            with unittest_mock.patch('sys.stdin', new=StringIO(TEST_VALUE)), \
                 unittest_mock.patch('sys.stdout', new=StringIO()) as stdout, \
                 unittest_mock.patch('sys.stderr', new=StringIO()) as stderr, \
                 unittest_mock.patch('sys.argv', argv):
                main()

        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), '')

    def test_validate_stdin_value_error(self):
        test_files = [
            ('test.smd', TEST_SCHEMA_MARKDOWN)
        ]
        with self.create_test_files(test_files) as input_dir:
            schema_path = os.path.join(input_dir, 'test.smd')
            argv = ['python3 -m schema_markdown', 'validate', schema_path, 'MyStruct']
            with unittest_mock.patch('sys.stdin', new=StringIO('{}')), \
                 unittest_mock.patch('sys.stdout', new=StringIO()), \
                 unittest_mock.patch('sys.stderr', new=StringIO()), \
                 unittest_mock.patch('sys.argv', argv):
                with self.assertRaises(ValidationError):
                    main()

    def test_validate_no_type(self):
        argv = ['python3 -m schema_markdown', 'validate']
        with unittest_mock.patch('sys.stdout', new=StringIO()) as stdout, \
             unittest_mock.patch('sys.stderr', new=StringIO()) as stderr, \
             unittest_mock.patch('sys.argv', argv):
            with self.assertRaises(SystemExit):
                main()

        self.assertEqual(stdout.getvalue(), '')
        self.assertTrue(stderr.getvalue().endswith('''\
schema_markdown validate: error: the following arguments are required: schema, type, paths
'''))

    def test_no_command(self):
        argv = ['python3 -m schema_markdown']
        with unittest_mock.patch('sys.stdout', new=StringIO()) as stdout, \
             unittest_mock.patch('sys.stderr', new=StringIO()) as stderr, \
             unittest_mock.patch('sys.argv', argv):
            with self.assertRaises(SystemExit):
                main()

        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), '''\
usage: schema_markdown [-h] {compile,validate} ...
schema_markdown: error: the following arguments are required: command
''')
