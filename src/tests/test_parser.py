# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/master/LICENSE

# pylint: disable=missing-docstring

import os

from schema_markdown import SchemaMarkdownParser, SchemaMarkdownParserError, validate_type_model_types

from . import TestCase


class TestSchemaMarkdownParser(TestCase):

    def _test_load_schema_markdown(self):
        return self.create_test_files((
            (
                'README.txt',
                ''
            ),
            (
                'module.scm',
                '''\
action my_action

action my_action2
    input
        int value
    output
        int result
'''
            ),
            (
                ('sub', 'subsub', 'submodule.scm'),
                '''\
action my_action3
    input
        int myArg
    output
        string myArg
'''
            )
        ))

    def test_load(self):
        with self._test_load_schema_markdown() as parser_dir:
            parser = SchemaMarkdownParser()
            parser.load(parser_dir)
            self.assertIn('my_action', parser.types)
            self.assertIn('my_action2', parser.types)
            self.assertIn('my_action3', parser.types)

    def test_load_file(self):
        with self._test_load_schema_markdown() as parser_dir:
            parser = SchemaMarkdownParser()
            parser.load(os.path.join(parser_dir, 'module.scm'))
            self.assertIn('my_action', parser.types)
            self.assertIn('my_action2', parser.types)
            self.assertNotIn('my_action3', parser.types)

    def test_load_finalize(self):
        with self._test_load_schema_markdown() as parser_dir:
            parser = SchemaMarkdownParser()
            parser.load(parser_dir, finalize=False)
            parser.finalize()
            self.assertIn('my_action', parser.types)
            self.assertIn('my_action2', parser.types)
            self.assertIn('my_action3', parser.types)

    def test_simple(self):
        parser = SchemaMarkdownParser()
        parser.parse_string('''\
# This is an enum
enum MyEnum
    Foo
    Bar
    "Foo and Bar"

# This is the struct
struct MyStruct

    # The 'a' member
    string a

    # The 'b' member
    int b

# This is the second struct
struct MyStruct2
    int a
    optional \\
        float b
    string(nullable) \\
        c
    bool d
    int[] e
    optional MyStruct[] f
    optional float{} g
    optional datetime h
    optional uuid i
    optional MyEnum : MyStruct{} j
    optional date(nullable) k
    optional object l

# This is a union
union MyUnion
    int a
    string b

# The action
action MyAction
    input
        int a
        optional string b
    output
        bool c
    errors
        Error1
        Error2
        "Error 3"

# The second action
action MyAction2
    query
        int a
    input
        MyStruct foo
        MyStruct2[] bar

# The third action
action MyAction3
    urls
        GET /MyAction3/{d}
    path
        int d
    output
        int a
        datetime b
        date c

# The fourth action
action MyAction4 \\
''')
        self.assertDictEqual(parser.types, {
            'MyAction': {
                'action': {
                    'name': 'MyAction',
                    'doc': ['The action'],
                    'errors': 'MyAction_errors',
                    'input': 'MyAction_input',
                    'output': 'MyAction_output'
                }
            },
            'MyAction_errors': {
                'enum': {
                    'name': 'MyAction_errors',
                    'values': [
                        {'name': 'Error1'},
                        {'name': 'Error2'},
                        {'name': 'Error 3'}
                    ]
                }
            },
            'MyAction_input': {
                'struct': {
                    'name': 'MyAction_input',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}},
                        {'name': 'b', 'optional': True, 'type': {'builtin': 'string'}}
                    ]
                }
            },
            'MyAction_output': {
                'struct': {
                    'name': 'MyAction_output',
                    'members': [
                        {'name': 'c', 'type': {'builtin': 'bool'}}
                    ]
                }
            },
            'MyAction2': {
                'action': {
                    'name': 'MyAction2',
                    'doc': ['The second action'],
                    'input': 'MyAction2_input',
                    'query': 'MyAction2_query'
                }
            },
            'MyAction2_input': {
                'struct': {
                    'name': 'MyAction2_input',
                    'members': [
                        {'name': 'foo', 'type': {'user': 'MyStruct'}},
                        {'name': 'bar', 'type': {'array': {'type': {'user': 'MyStruct2'}}}}
                    ]
                }
            },
            'MyAction2_query': {
                'struct': {
                    'name': 'MyAction2_query',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}}
                    ]
                }
            },
            'MyAction3': {
                'action': {
                    'name': 'MyAction3',
                    'doc': ['The third action'],
                    'output': 'MyAction3_output',
                    'path': 'MyAction3_path',
                    'urls': [
                        {'method': 'GET', 'path': '/MyAction3/{d}'}
                    ]
                }
            },
            'MyAction3_output': {
                'struct': {
                    'name': 'MyAction3_output',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}},
                        {'name': 'b', 'type': {'builtin': 'datetime'}},
                        {'name': 'c', 'type': {'builtin': 'date'}}
                    ]
                }
            },
            'MyAction3_path': {
                'struct': {
                    'name': 'MyAction3_path',
                    'members': [
                        {'name': 'd', 'type': {'builtin': 'int'}}
                    ]
                }
            },
            'MyAction4': {
                'action': {
                    'name': 'MyAction4',
                    'doc': ['The fourth action']
                }
            },
            'MyEnum': {
                'enum': {
                    'name': 'MyEnum',
                    'doc': ['This is an enum'],
                    'values': [
                        {'name': 'Foo'},
                        {'name': 'Bar'},
                        {'name': 'Foo and Bar'}
                    ]
                }
            },
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'doc': ['This is the struct'],
                    'members': [
                        {'doc': ["The 'a' member"], 'name': 'a', 'type': {'builtin': 'string'}},
                        {'doc': ["The 'b' member"], 'name': 'b', 'type': {'builtin': 'int'}}
                    ]
                }
            },
            'MyStruct2': {
                'struct': {
                    'name': 'MyStruct2',
                    'doc': ['This is the second struct'],
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}},
                        {'name': 'b', 'optional': True, 'type': {'builtin': 'float'}},
                        {'name': 'c', 'type': {'builtin': 'string'}, 'attr': {'nullable': True}},
                        {'name': 'd', 'type': {'builtin': 'bool'}},
                        {'name': 'e', 'type': {'array': {'type': {'builtin': 'int'}}}},
                        {'name': 'f', 'optional': True, 'type': {'array': {'type': {'user': 'MyStruct'}}}},
                        {'name': 'g', 'optional': True, 'type': {'dict': {'type': {'builtin': 'float'}}}},
                        {'name': 'h', 'optional': True, 'type': {'builtin': 'datetime'}},
                        {'name': 'i', 'optional': True, 'type': {'builtin': 'uuid'}},
                        {'name': 'j', 'optional': True,
                         'type': {'dict': {'keyType': {'user': 'MyEnum'}, 'type': {'user': 'MyStruct'}}}},
                        {'name': 'k', 'optional': True, 'type': {'builtin': 'date'}, 'attr': {'nullable': True}},
                        {'name': 'l', 'optional': True, 'type': {'builtin': 'object'}}
                    ]
                }
            },
            'MyUnion': {
                'struct': {
                    'name': 'MyUnion',
                    'doc': ['This is a union'],
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}},
                        {'name': 'b', 'type': {'builtin': 'string'}}
                    ],
                    'union': True
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_parse_defaults(self):
        parser = SchemaMarkdownParser()
        parser.parse([
            'struct MyStruct',
            '    int a',
            '    int b'
        ])
        self.assertDictEqual(parser.types, {
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}},
                        {'name': 'b', 'type': {'builtin': 'int'}}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_action_urls(self):
        parser = SchemaMarkdownParser('''\
action MyAction

action MyActionUrl
    urls
        GET
        GET /
        *
        * /star
''')
        self.assertDictEqual(parser.types, {
            'MyAction': {
                'action': {
                    'name': 'MyAction'
                }
            },
            'MyActionUrl': {
                'action': {
                    'name': 'MyActionUrl',
                    'urls': [
                        {'method': 'GET'},
                        {'method': 'GET', 'path': '/'},
                        {},
                        {'path': '/star'}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_action_url_duplicate(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action MyAction
    urls
        GET /
        GET /
        GET
        POST
        GET
    urls
        GET
''')
        expected_errors = [
            ':4: error: Duplicate URL: GET /',
            ':7: error: Duplicate URL: GET ',
            ':8: error: Redefinition of action urls'
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_action_url_typed(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action MyAction
    url (BaseType)
        GET /
''')
        expected_errors = [
            ':2: error: Syntax error',
            ':3: error: Syntax error'
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_group(self):
        parser = SchemaMarkdownParser('''\
action MyAction

enum MyEnum

struct MyStruct

typedef int MyTypedef

group "Stuff"

action MyAction2

enum MyEnum2

group "Other Stuff"

action MyAction3

struct MyStruct2

typedef int MyTypedef3

group

action MyAction4
''')
        self.assertDictEqual(parser.types, {
            'MyAction': {'action': {'name': 'MyAction'}},
            'MyAction2': {'action': {'docGroup': 'Stuff', 'name': 'MyAction2'}},
            'MyAction3': {'action': {'docGroup': 'Other Stuff', 'name': 'MyAction3'}},
            'MyAction4': {'action': {'name': 'MyAction4'}},
            'MyEnum': {'enum': {'name': 'MyEnum'}},
            'MyEnum2': {'enum': {'docGroup': 'Stuff', 'name': 'MyEnum2'}},
            'MyStruct': {'struct': {'name': 'MyStruct'}},
            'MyStruct2': {'struct': {'docGroup': 'Other Stuff', 'name': 'MyStruct2'}},
            'MyTypedef': {'typedef': {'name': 'MyTypedef', 'type': {'builtin': 'int'}}},
            'MyTypedef3': {'typedef': {'docGroup': 'Other Stuff', 'name': 'MyTypedef3', 'type': {'builtin': 'int'}}}
        })
        self.assertListEqual(parser.errors, [])

    def test_struct_base_types(self):
        parser = SchemaMarkdownParser('''\
struct MyStruct (MyStruct2)
    int c

struct MyStruct2 (MyStruct3)
    float b

struct MyStruct3
    string a

struct MyStruct4
    bool d

typedef MyStruct4 MyTypedef

struct MyStruct5 (MyStruct2, MyTypedef)
    datetime e
''')
        validate_type_model_types(parser.types)
        self.assertDictEqual(parser.types, {
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'bases': ['MyStruct2'],
                    'members': [
                        {'name': 'c', 'type': {'builtin': 'int'}}
                    ]
                }
            },
            'MyStruct2': {
                'struct': {
                    'name': 'MyStruct2',
                    'bases': ['MyStruct3'],
                    'members': [
                        {'name': 'b', 'type': {'builtin': 'float'}}
                    ]
                }
            },
            'MyStruct3': {
                'struct': {
                    'name': 'MyStruct3',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'string'}}
                    ]
                }
            },
            'MyStruct4': {
                'struct': {
                    'name': 'MyStruct4',
                    'members': [
                        {'name': 'd', 'type': {'builtin': 'bool'}}
                    ]
                }
            },
            'MyStruct5': {
                'struct': {
                    'name': 'MyStruct5',
                    'bases': ['MyStruct2', 'MyTypedef'],
                    'members': [
                        {'name': 'e', 'type': {'builtin': 'datetime'}}
                    ]
                }
            },
            'MyTypedef': {
                'typedef': {
                    'name': 'MyTypedef',
                    'type': {'user': 'MyStruct4'}
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_struct_base_types_error(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
struct MyStruct (MyEnum)
    int a

enum MyEnum
    A

struct MyStruct3 (MyStruct)
    string a

typedef string{} MyDict

struct MyStruct4
    int b

struct MyStruct5 (MyStruct4, MyDict)
    int b
''')
        self.assertListEqual(cm_exc.exception.errors, [
            ":1: error: Invalid struct base type 'MyEnum'",
            ":8: error: Redefinition of 'MyStruct3' member 'a'",
            ":15: error: Invalid struct base type 'MyDict'",
            ":16: error: Redefinition of 'MyStruct5' member 'b'"
        ])

    def test_struct_base_types_circular(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
struct MyStruct (MyStruct2)
    int a

struct MyStruct2 (MyStruct3)
    int b

struct MyStruct3 (MyStruct)
    int c
''')
        expected_errors = [
            ":1: error: Circular base type detected for type 'MyStruct'",
            ":4: error: Circular base type detected for type 'MyStruct2'",
            ":7: error: Circular base type detected for type 'MyStruct3'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_enum_base_types(self):
        parser = SchemaMarkdownParser('''\
enum MyEnum (MyEnum2)
    c

enum MyEnum2 (MyEnum3)
    b

enum MyEnum3
    a

enum MyEnum4
    d

typedef MyEnum4 MyTypedef

enum MyEnum5 (MyEnum2, MyTypedef)
    e
''')
        self.assertDictEqual(parser.types, {
            'MyEnum': {'enum': {'bases': ['MyEnum2'], 'name': 'MyEnum', 'values': [{'name': 'c'}]}},
            'MyEnum2': {'enum': {'bases': ['MyEnum3'], 'name': 'MyEnum2', 'values': [{'name': 'b'}]}},
            'MyEnum3': {'enum': {'name': 'MyEnum3', 'values': [{'name': 'a'}]}},
            'MyEnum4': {'enum': {'name': 'MyEnum4', 'values': [{'name': 'd'}]}},
            'MyEnum5': {'enum': {'bases': ['MyEnum2', 'MyTypedef'], 'name': 'MyEnum5', 'values': [{'name': 'e'}]}},
            'MyTypedef': {'typedef': {'name': 'MyTypedef', 'type': {'user': 'MyEnum4'}}}
        })
        self.assertListEqual(parser.errors, [])

    def test_enum_base_types_error(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
enum MyEnum (MyStruct)
    A

struct MyStruct
    int a

enum MyEnum3 (MyEnum)
    A

typedef string{} MyDict

enum MyEnum4
    B

enum MyEnum5 (MyEnum4, MyDict)
    B
''')
        self.assertListEqual(cm_exc.exception.errors, [
            ":1: error: Invalid enum base type 'MyStruct'",
            ":8: error: Redefinition of 'MyEnum3' value 'A'",
            ":15: error: Invalid enum base type 'MyDict'",
            ":16: error: Redefinition of 'MyEnum5' value 'B'"
        ])

    def test_enum_base_types_circular(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
enum MyEnum (MyEnum2)
    a

enum MyEnum2 (MyEnum3)
    b

enum MyEnum3 (MyEnum)
    c
''')
        expected_errors = [
            ":1: error: Circular base type detected for type 'MyEnum'",
            ":4: error: Circular base type detected for type 'MyEnum2'",
            ":7: error: Circular base type detected for type 'MyEnum3'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_multiple(self):
        parser = SchemaMarkdownParser()
        parser.parse_string('''\
enum MyEnum
    A
    B

action MyAction
    input
        MyStruct2 a
    output
        MyStruct b
        MyEnum2 c

struct MyStruct
    string c
    MyEnum2 d
    MyStruct2 e
''', finalize=False)
        parser.parse_string('''\
action MyAction2
    input
        MyStruct d
    output
        MyStruct2 e

struct MyStruct2
    string f
    MyEnum2 g

enum MyEnum2
    C
    D
''')
        self.assertDictEqual(parser.types, {
            'MyAction': {
                'action': {
                    'name': 'MyAction',
                    'input': 'MyAction_input',
                    'output': 'MyAction_output'
                }
            },
            'MyAction_input': {
                'struct': {
                    'name': 'MyAction_input',
                    'members': [
                        {'name': 'a', 'type': {'user': 'MyStruct2'}}
                    ]
                }
            },
            'MyAction_output': {
                'struct': {
                    'name': 'MyAction_output',
                    'members': [
                        {'name': 'b', 'type': {'user': 'MyStruct'}},
                        {'name': 'c', 'type': {'user': 'MyEnum2'}}
                    ]
                }
            },
            'MyAction2': {
                'action': {
                    'name': 'MyAction2',
                    'input': 'MyAction2_input',
                    'output': 'MyAction2_output'
                }
            },
            'MyAction2_input': {
                'struct': {
                    'name': 'MyAction2_input',
                    'members': [
                        {'name': 'd', 'type': {'user': 'MyStruct'}}
                    ]
                }
            },
            'MyAction2_output': {
                'struct': {
                    'name': 'MyAction2_output',
                    'members': [
                        {'name': 'e', 'type': {'user': 'MyStruct2'}}
                    ]
                }
            },
            'MyEnum': {
                'enum': {
                    'name': 'MyEnum',
                    'values': [
                        {'name': 'A'},
                        {'name': 'B'}
                    ]
                }
            },
            'MyEnum2': {
                'enum': {
                    'name': 'MyEnum2',
                    'values': [
                        {'name': 'C'},
                        {'name': 'D'}
                    ]
                }
            },
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {'name': 'c', 'type': {'builtin': 'string'}},
                        {'name': 'd', 'type': {'user': 'MyEnum2'}},
                        {'name': 'e', 'type': {'user': 'MyStruct2'}}
                    ]
                }
            },
            'MyStruct2': {
                'struct': {
                    'name': 'MyStruct2',
                    'members': [
                        {'name': 'f', 'type': {'builtin': 'string'}},
                        {'name': 'g', 'type': {'user': 'MyEnum2'}}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_multiple_finalize(self):
        parser = SchemaMarkdownParser('''\
struct MyStruct
    MyEnum a

enum MyEnum
    A
    B
''')
        parser.parse_string('''\
struct MyStruct2
    int a
    MyEnum b
    MyEnum2 c

enum MyEnum2
    C
    D
''')
        self.assertDictEqual(parser.types, {
            'MyEnum': {
                'enum': {
                    'name': 'MyEnum',
                    'values': [
                        {'name': 'A'},
                        {'name': 'B'}
                    ]
                }
            },
            'MyEnum2': {
                'enum': {
                    'name': 'MyEnum2',
                    'values': [
                        {'name': 'C'},
                        {'name': 'D'}
                    ]
                }
            },
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {'name': 'a', 'type': {'user': 'MyEnum'}}
                    ]
                }
            },
            'MyStruct2': {
                'struct': {
                    'name': 'MyStruct2',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}},
                        {'name': 'b', 'type': {'user': 'MyEnum'}},
                        {'name': 'c', 'type': {'user': 'MyEnum2'}}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_array_attr(self):
        parser = SchemaMarkdownParser('''\
struct MyStruct
    MyStruct2[len > 0] a
struct MyStruct2
''')
        self.assertDictEqual(parser.types, {
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {'attr': {'lenGT': 0}, 'name': 'a', 'type': {'array': {'type': {'user': 'MyStruct2'}}}}
                    ]
                }
            },
            'MyStruct2': {
                'struct': {'name': 'MyStruct2'}
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_dict_attr(self):
        parser = SchemaMarkdownParser('''\
struct MyStruct
    MyEnum : MyStruct2{len > 0} a
enum MyEnum
struct MyStruct2
''')
        self.assertDictEqual(parser.types, {
            'MyEnum': {
                'enum': {
                    'name': 'MyEnum'
                }
            },
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {'attr': {'lenGT': 0}, 'name': 'a',
                         'type': {'dict': {'keyType': {'user': 'MyEnum'}, 'type': {'user': 'MyStruct2'}}}}
                    ]
                }
            },
            'MyStruct2': {
                'struct': {
                    'name': 'MyStruct2'
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_nullable(self):
        parser = SchemaMarkdownParser('''\
struct MyStruct
    int(nullable) a
    float[nullable] b
    float(nullable)[nullable] c
    bool{nullable} d
    bool(nullable){nullable} e
    string(nullable) : date{} f

typedef string(nullable) MyTypedef
''')
        self.assertDictEqual(parser.types, {
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}, 'attr': {'nullable': True}},
                        {'name': 'b', 'type': {'array': {'type': {'builtin': 'float'}}}, 'attr': {'nullable': True}},
                        {
                            'name': 'c',
                            'type': {'array': {'type': {'builtin': 'float'}, 'attr': {'nullable': True}}},
                            'attr': {'nullable': True}
                        },
                        {'name': 'd', 'type': {'dict': {'type': {'builtin': 'bool'}}}, 'attr': {'nullable': True}},
                        {
                            'name': 'e',
                            'type': {'dict': {'type': {'builtin': 'bool'}, 'attr': {'nullable': True}}},
                            'attr': {'nullable': True}
                        },
                        {'name': 'f',
                         'type': {
                             'dict': {
                                 'type': {'builtin': 'date'},
                                 'keyType': {'builtin': 'string'},
                                 'keyAttr': {'nullable': True}
                             }
                         }
                        }
                    ]
                }
            },
            'MyTypedef': {
                'typedef': {'name': 'MyTypedef', 'type': {'builtin': 'string'}, 'attr': {'nullable': True}}
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_nullable_with_attr(self):
        parser = SchemaMarkdownParser('''\
struct MyStruct
    int(nullable, > 0) a
''')
        self.assertDictEqual(parser.types, {
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}, 'attr': {'gt': 0.0, 'nullable': True}}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_invalid_attr(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
struct MyStruct
    MyStruct2(len > 0) a
struct MyStruct2
''')
        expected_errors = [
            ":2: error: Invalid attribute 'len > 0' from 'MyStruct' member 'a'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_error_unknown_type(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
struct Foo
    MyBadType a

action MyAction
    input
        MyBadType2 a
    output
        MyBadType b
''', filename='foo')
        expected_errors = [
            "foo:2: error: Unknown type 'MyBadType' from 'Foo' member 'a'",
            "foo:6: error: Unknown type 'MyBadType2' from 'MyAction_input' member 'a'",
            "foo:8: error: Unknown type 'MyBadType' from 'MyAction_output' member 'b'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_error_unknown_array_type(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
struct MyStruct
    MyBadType[] a
    MyTypedef[] b

typedef MyBadType MyTypedef
''', filename='foo')
        expected_errors = [
            "foo:2: error: Unknown type 'MyBadType' from 'MyStruct' member 'a'",
            "foo:3: error: Unknown type 'MyBadType' from 'MyStruct' member 'b'",
            "foo:5: error: Unknown type 'MyBadType' from 'MyTypedef'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_error_unknown_dict_type(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
struct MyStruct
    MyBadType{} a
    MyTypedef{} b

typedef MyBadType MyTypedef
''', filename='foo')
        expected_errors = [
            "foo:2: error: Unknown type 'MyBadType' from 'MyStruct' member 'a'",
            "foo:3: error: Unknown type 'MyBadType' from 'MyStruct' member 'b'",
            "foo:5: error: Unknown type 'MyBadType' from 'MyTypedef'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_error_unknown_dict_key_type(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
struct MyStruct
    MyBadType : int{} a
    MyTypedef : int{} b

typedef MyBadType MyTypedef
''', filename='foo')
        expected_errors = [
            "foo:2: error: Invalid dictionary key type from 'MyStruct' member 'a'",
            "foo:2: error: Unknown type 'MyBadType' from 'MyStruct' member 'a'",
            "foo:3: error: Invalid dictionary key type from 'MyStruct' member 'b'",
            "foo:3: error: Unknown type 'MyBadType' from 'MyStruct' member 'b'",
            "foo:5: error: Unknown type 'MyBadType' from 'MyTypedef'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_error_action_type(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
struct Foo
    MyAction a

action MyAction
''', filename='foo')
        expected_errors = [
            "foo:2: error: Invalid reference to action 'MyAction' from 'Foo' member 'a'",
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_error_struct_redefinition(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
struct Foo
    int a

enum Foo
    A
    B
''')
        self.assertEqual(str(cm_exc.exception), ":4: error: Redefinition of type 'Foo'")
        self.assertDictEqual(parser.types, {
            'Foo': {'enum': {'name': 'Foo', 'values': [{'name': 'A'}, {'name': 'B'}]}}
        })
        self.assertListEqual(parser.errors, [
            ":4: error: Redefinition of type 'Foo'"
        ])

    def test_error_enum_redefinition(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
enum Foo
    A
    B

struct Foo
    int a
''')
        self.assertEqual(str(cm_exc.exception), ":5: error: Redefinition of type 'Foo'")
        self.assertDictEqual(parser.types, {
            'Foo': {
                'struct': {
                    'name': 'Foo',
                    'members': [{'name': 'a', 'type': {'builtin': 'int'}}]
                }
            }
        })
        self.assertListEqual(parser.errors, [
            ":5: error: Redefinition of type 'Foo'"
        ])

    def test_error_typedef_redefinition(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
struct Foo
    int a

typedef int(> 5) Foo
''')
        self.assertEqual(str(cm_exc.exception), ":4: error: Redefinition of type 'Foo'")
        self.assertDictEqual(parser.types, {
            'Foo': {'typedef': {'attr': {'gt': 5.0}, 'name': 'Foo', 'type': {'builtin': 'int'}}}
        })
        self.assertListEqual(parser.errors, [
            ":4: error: Redefinition of type 'Foo'"
        ])

    def test_error_action_redefinition(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action MyAction
    input
        int a

action MyAction
    input
        string b
''')
        self.assertEqual(str(cm_exc.exception), ":5: error: Redefinition of action 'MyAction'")
        self.assertDictEqual(parser.types, {
            'MyAction': {
                'action': {
                    'name': 'MyAction',
                    'input': 'MyAction_input'
                }
            },
            'MyAction_input': {
                'struct': {
                    'name': 'MyAction_input',
                    'members': [
                        {'name': 'b', 'type': {'builtin': 'string'}}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [
            ":5: error: Redefinition of action 'MyAction'"
        ])

    def test_error_action_section(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action MyAction

struct MyStruct
    int a

    input
    output
    errors

input
output
errors
''')
        self.assertEqual(str(cm_exc.exception), '''\
:6: error: Syntax error
:7: error: Syntax error
:8: error: Syntax error
:10: error: Syntax error
:11: error: Syntax error
:12: error: Syntax error''')
        self.assertDictEqual(parser.types, {
            'MyAction': {'action': {'name': 'MyAction'}},
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [
            ':6: error: Syntax error',
            ':7: error: Syntax error',
            ':8: error: Syntax error',
            ':10: error: Syntax error',
            ':11: error: Syntax error',
            ':12: error: Syntax error'
        ])

    def test_error_member(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action MyAction
    int abc

struct MyStruct

enum MyEnum

    int bcd

int cde
''')
        self.assertEqual(str(cm_exc.exception), '''\
:2: error: Syntax error
:8: error: Syntax error
:10: error: Syntax error''')
        self.assertDictEqual(parser.types, {
            'MyAction': {'action': {'name': 'MyAction'}},
            'MyEnum': {'enum': {'name': 'MyEnum'}},
            'MyStruct': {'struct': {'name': 'MyStruct'}}
        })
        self.assertListEqual(parser.errors, [
            ':2: error: Syntax error',
            ':8: error: Syntax error',
            ':10: error: Syntax error'
        ])

    def test_error_enum(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
enum MyEnum
    "abc
    abc"
Value1

struct MyStruct

    Value2

action MyAction
    input
        MyError
''')
        self.assertEqual(str(cm_exc.exception), '''\
:2: error: Syntax error
:3: error: Syntax error
:4: error: Syntax error
:8: error: Syntax error
:12: error: Syntax error''')
        self.assertDictEqual(parser.types, {
            'MyAction': {
                'action': {
                    'name': 'MyAction',
                    'input': 'MyAction_input'
                }
            },
            'MyAction_input': {
                'struct': {
                    'name': 'MyAction_input'
                }
            },
            'MyEnum': {
                'enum': {'name': 'MyEnum'}
            },
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct'
                }
            }
        })
        self.assertListEqual(parser.errors, [
            ':2: error: Syntax error',
            ':3: error: Syntax error',
            ':4: error: Syntax error',
            ':8: error: Syntax error',
            ':12: error: Syntax error'
        ])

    def test_attributes(self):
        parser = SchemaMarkdownParser()
        parser.parse_string('''\
struct MyStruct
    optional int(> 1,<= 10.5) i1
    optional int (>= 1, < 10 ) i2
    int( > 0, <= 10) i3
    int(> -4, < -1.4) i4
    int(== 5) i5
    float( > 1, <= 10.5) f1
    float(>= 1.5, < 10 ) f2
    string(len > 5, len < 101) s1
    string( len >= 5, len <= 100 ) s2
    string( len == 2 ) s3
    int(> 5)[] ai1
    string(len < 5)[len < 10] as1
    string(len == 2)[len == 3] as2
    int(< 15){} di1
    string(len > 5){len > 10} ds1
    string(len == 2){len == 3} ds2
    string(len == 1) : string(len == 2){len == 3} ds3
''', filename='foo')
        self.assertDictEqual(parser.types, {
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {
                            'name': 'i1',
                            'type': {'builtin': 'int'},
                            'attr': {'gt': 1.0, 'lte': 10.5},
                            'optional': True
                        },
                        {
                            'name': 'i2',
                            'type': {'builtin': 'int'},
                            'attr': {'gte': 1.0, 'lt': 10.0},
                            'optional': True
                        },
                        {
                            'name': 'i3',
                            'type': {'builtin': 'int'},
                            'attr': {'gt': 0.0, 'lte': 10.0}
                        },
                        {
                            'name': 'i4',
                            'type': {'builtin': 'int'},
                            'attr': {'gt': -4.0, 'lt': -1.4}
                        },
                        {
                            'name': 'i5',
                            'type': {'builtin': 'int'},
                            'attr': {'eq': 5.0}
                        },
                        {
                            'name': 'f1',
                            'type': {'builtin': 'float'},
                            'attr': {'gt': 1.0, 'lte': 10.5}
                        },
                        {
                            'name': 'f2',
                            'type': {'builtin': 'float'},
                            'attr': {'gte': 1.5, 'lt': 10.0}
                        },
                        {
                            'name': 's1',
                            'type': {'builtin': 'string'},
                            'attr': {'lenGT': 5, 'lenLT': 101}
                        },
                        {
                            'name': 's2',
                            'type': {'builtin': 'string'},
                            'attr': {'lenGTE': 5, 'lenLTE': 100}
                        },
                        {
                            'name': 's3',
                            'type': {'builtin': 'string'},
                            'attr': {'lenEq': 2}
                        },
                        {
                            'name': 'ai1',
                            'type': {'array': {'attr': {'gt': 5.0}, 'type': {'builtin': 'int'}}}
                        },
                        {
                            'name': 'as1',
                            'type': {'array': {'attr': {'lenLT': 5}, 'type': {'builtin': 'string'}}},
                            'attr': {'lenLT': 10}
                        },
                        {
                            'name': 'as2',
                            'type': {'array': {'attr': {'lenEq': 2}, 'type': {'builtin': 'string'}}},
                            'attr': {'lenEq': 3}
                        },
                        {
                            'name': 'di1',
                            'type': {'dict': {'attr': {'lt': 15.0}, 'type': {'builtin': 'int'}}}
                        },
                        {
                            'name': 'ds1',
                            'type': {'dict': {'attr': {'lenGT': 5}, 'type': {'builtin': 'string'}}},
                            'attr': {'lenGT': 10}
                        },
                        {
                            'name': 'ds2',
                            'type': {'dict': {'attr': {'lenEq': 2}, 'type': {'builtin': 'string'}}},
                            'attr': {'lenEq': 3}
                        },
                        {
                            'attr': {'lenEq': 3},
                            'name': 'ds3',
                            'type': {
                                'dict': {
                                    'attr': {'lenEq': 2},
                                    'keyAttr': {'lenEq': 1},
                                    'keyType': {'builtin': 'string'},
                                    'type': {'builtin': 'string'}
                                }
                            }
                        }
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def _test_parser_error(self, errors, text):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string(text)
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertEqual(len(parser.errors), len(errors))
        self.assertListEqual(parser.errors, errors)

    def test_error_attribute_eq(self):
        self._test_parser_error([":2: error: Invalid attribute '== 7' from 'MyStruct' member 's'"], '''\
struct MyStruct
    string(== 7) s
''')

    def test_error_attribute_lt(self):
        self._test_parser_error([":2: error: Invalid attribute '< 7' from 'MyStruct' member 's'"], '''\
struct MyStruct
    string(< 7) s
''')

    def test_error_attribute_gt(self):
        self._test_parser_error([":2: error: Invalid attribute '> 7' from 'MyStruct' member 's'"], '''\
struct MyStruct
    string(> 7) s
''')

    def test_error_attribute_lt_gt(self):
        self._test_parser_error([":2: error: Invalid attribute '< 7' from 'MyStruct' member 's'",
                               ":2: error: Invalid attribute '> 7' from 'MyStruct' member 's'"], '''\
struct MyStruct
    string(< 7, > 7) s
''')

    def test_error_attribute_lte_gte(self):
        self._test_parser_error([":6: error: Invalid attribute '>= 1' from 'MyStruct' member 'a'",
                               ":7: error: Invalid attribute '<= 2' from 'MyStruct' member 'b'"], '''\
enum MyEnum
    Foo
    Bar

struct MyStruct
    MyStruct(>= 1) a
    MyEnum(<= 2) b
''')

    def test_error_attribute_len_eq(self):
        self._test_parser_error([":2: error: Invalid attribute 'len == 1' from 'MyStruct' member 'i'"], '''\
struct MyStruct
    int(len == 1) i
''')

    def test_error_attribute_len_lt(self):
        self._test_parser_error([":2: error: Invalid attribute 'len < 10' from 'MyStruct' member 'f'"], '''\
struct MyStruct
    float(len < 10) f
''')

    def test_error_attribute_len_gt(self):
        self._test_parser_error([":2: error: Invalid attribute 'len > 1' from 'MyStruct' member 'i'"], '''\
struct MyStruct
    int(len > 1) i
''')

    def test_error_attribute_len_lt_gt(self):
        self._test_parser_error([":2: error: Invalid attribute 'len < 10' from 'MyStruct' member 'f'",
                               ":2: error: Invalid attribute 'len > 10' from 'MyStruct' member 'f'"], '''\
struct MyStruct
    float(len < 10, len > 10) f
''')

    def test_error_attribute_len_lte_gte(self):
        self._test_parser_error([":2: error: Invalid attribute 'len <= 10' from 'MyStruct' member 'f'",
                               ":3: error: Invalid attribute 'len >= 10' from 'MyStruct' member 'f2'"], '''\
struct MyStruct
    float(len <= 10) f
    float(len >= 10) f2
''')

    def test_error_attribute_invalid(self):
        self._test_parser_error([':2: error: Syntax error'], '''\
struct MyStruct
    string(regex="abc") a
''')

    def test_error_member_invalid(self):
        self._test_parser_error([':1: error: Syntax error',
                               ':5: error: Syntax error'], '''\
    string a

enum MyEnum
    Foo
    int b
''')

    def test_error_member_redefinition(self):
        self._test_parser_error([":4: error: Redefinition of 'MyStruct' member 'b'"], '''\
struct MyStruct
    string b
    int a
    float b
''')

    def test_error_enum_duplicate_value(self):
        self._test_parser_error([":4: error: Redefinition of 'MyEnum' value 'bar'"], '''\
enum MyEnum
    bar
    foo
    bar
''')

    def test_doc(self):
        parser = SchemaMarkdownParser()
        parser.parse_string('''\
# My enum
enum MyEnum

  # MyEnum value 1
  MyEnumValue1

  #
  # MyEnum value 2
  #
  # Second line
  #
  MyEnumValue2

#- Hidden comment
enum MyEnum2

  #- Hidden comment
  MyEnum2Value1

# My struct
struct MyStruct

  # MyStruct member a
  int a

  #
  # MyStruct member b
  #
  string[] b

#- Hidden comment
struct MyStruct2

  #- Hidden comment
  int a

# My action
action MyAction

  input

    # My input member
    float a

  output

    # My output member
    datetime b
''')
        self.assertDictEqual(parser.types, {
            'MyAction': {
                'action': {
                    'name': 'MyAction',
                    'doc': ['My action'],
                    'input': 'MyAction_input',
                    'output': 'MyAction_output'
                }
            },
            'MyAction_input': {
                'struct': {
                    'name': 'MyAction_input',
                    'members': [
                        {'doc': ['My input member'], 'name': 'a', 'type': {'builtin': 'float'}}
                    ]
                }
            },
            'MyAction_output': {
                'struct': {
                    'name': 'MyAction_output',
                    'members': [
                        {'doc': ['My output member'], 'name': 'b', 'type': {'builtin': 'datetime'}}
                    ]
                }
            },
            'MyEnum': {
                'enum': {
                    'name': 'MyEnum',
                    'doc': ['My enum'],
                    'values': [
                        {'doc': ['MyEnum value 1'], 'name': 'MyEnumValue1'},
                        {'doc': ['', 'MyEnum value 2', '', 'Second line', ''], 'name': 'MyEnumValue2'}
                    ]
                }
            },
            'MyEnum2': {
                'enum': {
                    'name': 'MyEnum2',
                    'values': [
                        {'name': 'MyEnum2Value1'}
                    ]
                }
            },
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'doc': ['My struct'],
                    'members': [
                        {'doc': ['MyStruct member a'], 'name': 'a', 'type': {'builtin': 'int'}},
                        {'doc': ['', 'MyStruct member b', ''], 'name': 'b', 'type': {'array': {'type': {'builtin': 'string'}}}}
                    ]
                }
            },
            'MyStruct2': {
                'struct': {
                    'name': 'MyStruct2',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_typedef(self):
        parser = SchemaMarkdownParser()
        parser.parse_string('''\
typedef MyEnum MyTypedef2

enum MyEnum
    A
    B

# My typedef
typedef MyEnum : MyStruct{len > 0} MyTypedef

struct MyStruct
    int a
    optional int b
''')
        self.assertDictEqual(parser.types, {
            'MyEnum': {
                'enum': {
                    'name': 'MyEnum',
                    'values': [
                        {'name': 'A'},
                        {'name': 'B'}
                    ]
                }
            },
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}},
                        {'name': 'b', 'optional': True, 'type': {'builtin': 'int'}}
                    ]
                }
            },
            'MyTypedef': {
                'typedef': {
                    'name': 'MyTypedef',
                    'doc': ['My typedef'],
                    'type': {'dict': {'keyType': {'user': 'MyEnum'}, 'type': {'user': 'MyStruct'}}},
                    'attr': {'lenGT': 0}
                }
            },
            'MyTypedef2': {
                'typedef': {
                    'name': 'MyTypedef2',
                    'type': {'user': 'MyEnum'}
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_error_dict_non_string_key(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
struct Foo
    int : int {} a
''')
        expected_errors = [
            ":2: error: Invalid dictionary key type from 'Foo' member 'a'",
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_error_action_section_redefinition(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action Foo
    urls
        POST
    path
        int a
    query
        int b
    input
        int c
    output
        int e

    urls
        GET
    path
        int a2
    query
        int b2
    input
        optional int c2
    output
        int e2
''')
        expected_errors = [
            ':13: error: Redefinition of action urls',
            ':15: error: Redefinition of action path',
            ':17: error: Redefinition of action query',
            ':19: error: Redefinition of action input',
            ':21: error: Redefinition of action output'
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_error_action_input_member_redefinition(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action MyAction
    path
        int a
        int b
    query
        int a
    input
        int b

action MyAction2
    path (Base)
    query
        int a
    input
        int b

struct Base
    int a
    int b
''')
        expected_errors = [
            ":3: error: Redefinition of 'MyAction_path' member 'a'",
            ":4: error: Redefinition of 'MyAction_path' member 'b'",
            ":6: error: Redefinition of 'MyAction_query' member 'a'",
            ":8: error: Redefinition of 'MyAction_input' member 'b'",
            ":11: error: Redefinition of 'MyAction2_path' member 'a'",
            ":11: error: Redefinition of 'MyAction2_path' member 'b'",
            ":13: error: Redefinition of 'MyAction2_query' member 'a'",
            ":15: error: Redefinition of 'MyAction2_input' member 'b'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_action_path_base_types(self):
        parser = SchemaMarkdownParser()
        parser.parse_string('''\
struct Foo
    int a
    optional string b

struct Bonk
    float(nullable) c

typedef Bonk Bar

action FooAction
    path (Foo)
        bool c

action BarAction
    path (Foo, Bar)
        datetime d
''')
        self.assertDictEqual(parser.types, {
            'Bar': {
                'typedef': {
                    'name': 'Bar',
                    'type': {'user': 'Bonk'}
                }
            },
            'BarAction': {
                'action': {
                    'name': 'BarAction',
                    'path': 'BarAction_path'
                }
            },
            'BarAction_path': {
                'struct': {
                    'name': 'BarAction_path',
                    'bases': ['Foo', 'Bar'],
                    'members': [
                        {'name': 'd', 'type': {'builtin': 'datetime'}}
                    ]
                }
            },
            'Bonk': {
                'struct': {
                    'name': 'Bonk',
                    'members': [
                        {'name': 'c', 'type': {'builtin': 'float'}, 'attr': {'nullable': True}}
                    ]
                }
            },
            'Foo': {
                'struct': {
                    'name': 'Foo',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}},
                        {'name': 'b', 'optional': True, 'type': {'builtin': 'string'}}
                    ]
                }
            },
            'FooAction': {
                'action': {
                    'name': 'FooAction',
                    'path': 'FooAction_path'
                }
            },
            'FooAction_path': {
                'struct': {
                    'name': 'FooAction_path',
                    'bases': ['Foo'],
                    'members': [
                        {'name': 'c', 'type': {'builtin': 'bool'}}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_action_path_non_struct(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action FooAction
    path (Foo)
        #- will not error
        float a

enum Foo
    A
    B

struct MyStruct
    int a

action BarAction
    path (Foo, MyStruct)

union MyUnion

action BonkAction
    path (MyStruct, MyUnion)
        float a

typedef string{} MyDict

action MyDictAction
    path (MyDict)
        int a
''')
        expected_errors = [
            ":2: error: Invalid struct base type 'Foo'",
            ":14: error: Invalid struct base type 'Foo'",
            ":19: error: Invalid struct base type 'MyUnion'",
            ":20: error: Redefinition of 'BonkAction_path' member 'a'",
            ":25: error: Invalid struct base type 'MyDict'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_action_query_base_types(self):
        parser = SchemaMarkdownParser()
        parser.parse_string('''\
struct Foo
    int a
    optional string b

struct Bonk
    float(nullable) c

typedef Bonk Bar

action FooAction
    query (Foo)
        bool c

action BarAction
    query (Foo, Bar)
        datetime d
''')
        self.assertDictEqual(parser.types, {
            'Bar': {
                'typedef': {
                    'name': 'Bar',
                    'type': {'user': 'Bonk'}
                }
            },
            'BarAction': {
                'action': {
                    'name': 'BarAction',
                    'query': 'BarAction_query'
                }
            },
            'BarAction_query': {
                'struct': {
                    'name': 'BarAction_query',
                    'bases': ['Foo', 'Bar'],
                    'members': [
                        {'name': 'd', 'type': {'builtin': 'datetime'}}
                    ]
                }
            },
            'Bonk': {
                'struct': {
                    'name': 'Bonk',
                    'members': [
                        {'name': 'c', 'type': {'builtin': 'float'}, 'attr': {'nullable': True}}
                    ]
                }
            },
            'Foo': {
                'struct': {
                    'name': 'Foo',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}},
                        {'name': 'b', 'optional': True, 'type': {'builtin': 'string'}}
                    ]
                }
            },
            'FooAction': {
                'action': {
                    'name': 'FooAction',
                    'query': 'FooAction_query'
                }
            },
            'FooAction_query': {
                'struct': {
                    'name': 'FooAction_query',
                    'bases': ['Foo'],
                    'members': [
                        {'name': 'c', 'type': {'builtin': 'bool'}}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_action_query_non_struct(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action FooAction
    query (Foo)
        #- will not error
        float a

enum Foo
    A
    B

struct MyStruct
    int a

action BarAction
    query (Foo, MyStruct)

union MyUnion

action BonkAction
    query (MyStruct, MyUnion)
        float a

typedef string{} MyDict

action MyDictAction
    query (MyDict)
        int a
''')
        expected_errors = [
            ":2: error: Invalid struct base type 'Foo'",
            ":14: error: Invalid struct base type 'Foo'",
            ":19: error: Invalid struct base type 'MyUnion'",
            ":20: error: Redefinition of 'BonkAction_query' member 'a'",
            ":25: error: Invalid struct base type 'MyDict'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_action_input_base_types(self):
        parser = SchemaMarkdownParser()
        parser.parse_string('''\
struct Foo
    int a
    optional string b

struct Bonk
    float(nullable) c

typedef Bonk Bar

action FooAction
    input (Foo)
        bool c

action BarAction
    input (Foo, Bar)
        datetime d
''')
        self.assertDictEqual(parser.types, {
            'Bar': {
                'typedef': {
                    'name': 'Bar',
                    'type': {'user': 'Bonk'}
                }
            },
            'BarAction': {
                'action': {
                    'name': 'BarAction',
                    'input': 'BarAction_input'
                }
            },
            'BarAction_input': {
                'struct': {
                    'name': 'BarAction_input',
                    'bases': ['Foo', 'Bar'],
                    'members': [
                        {'name': 'd', 'type': {'builtin': 'datetime'}}
                    ]
                }
            },
            'Bonk': {
                'struct': {
                    'name': 'Bonk',
                    'members': [
                        {'name': 'c', 'type': {'builtin': 'float'}, 'attr': {'nullable': True}}
                    ]
                }
            },
            'Foo': {
                'struct': {
                    'name': 'Foo',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}},
                        {'name': 'b', 'optional': True, 'type': {'builtin': 'string'}}
                    ]
                }
            },
            'FooAction': {
                'action': {
                    'name': 'FooAction',
                    'input': 'FooAction_input'
                }
            },
            'FooAction_input': {
                'struct': {
                    'name': 'FooAction_input',
                    'bases': ['Foo'],
                    'members': [
                        {'name': 'c', 'type': {'builtin': 'bool'}}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_action_input_non_struct(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action FooAction
    input (Foo)
        #- will not error
        float a

enum Foo
    A
    B

struct MyStruct
    int a

action BarAction
    input (Foo, MyStruct)

union MyUnion

action BonkAction
    input (MyStruct, MyUnion)
        float a

typedef string{} MyDict

action MyDictAction
    input (MyDict)
        int a
''')
        expected_errors = [
            ":2: error: Invalid struct base type 'Foo'",
            ":14: error: Invalid struct base type 'Foo'",
            ":19: error: Invalid struct base type 'MyUnion'",
            ":20: error: Redefinition of 'BonkAction_input' member 'a'",
            ":25: error: Invalid struct base type 'MyDict'",
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_action_input_member_redef(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action FooAction
    input (Foo)
        #- will not error
        float a

enum Foo
    A
    B

struct MyStruct
    int a

action BarAction
    input (Foo, MyStruct)

union MyUnion

action BonkAction
    input (MyStruct, MyUnion)
        float a

typedef string{} MyDict

action MyDictAction
    input (MyDict)
        int a
''')
        expected_errors = [
            ":2: error: Invalid struct base type 'Foo'",
            ":14: error: Invalid struct base type 'Foo'",
            ":19: error: Invalid struct base type 'MyUnion'",
            ":20: error: Redefinition of 'BonkAction_input' member 'a'",
            ":25: error: Invalid struct base type 'MyDict'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_action_output_struct(self):
        parser = SchemaMarkdownParser()
        parser.parse_string('''\
struct Foo
    int a
    optional string b

struct Bonk
    float(nullable) c

typedef Bonk Bar

action FooAction
    output (Foo)
        bool c

action BarAction
    output (Foo, Bar)
        datetime d
''')
        self.assertDictEqual(parser.types, {
            'Bar': {
                'typedef': {
                    'name': 'Bar',
                    'type': {'user': 'Bonk'}
                }
            },
            'BarAction': {
                'action': {
                    'name': 'BarAction',
                    'output': 'BarAction_output'
                }
            },
            'BarAction_output': {
                'struct': {
                    'name': 'BarAction_output',
                    'bases': ['Foo', 'Bar'],
                    'members': [
                        {'name': 'd', 'type': {'builtin': 'datetime'}}
                    ]
                }
            },
            'Bonk': {
                'struct': {
                    'name': 'Bonk',
                    'members': [
                        {'name': 'c', 'type': {'builtin': 'float'}, 'attr': {'nullable': True}}
                    ]
                }
            },
            'Foo': {
                'struct': {
                    'name': 'Foo',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}},
                        {'name': 'b', 'optional': True, 'type': {'builtin': 'string'}}
                    ]
                }
            },
            'FooAction': {
                'action': {
                    'name': 'FooAction',
                    'output': 'FooAction_output'
                }
            },
            'FooAction_output': {
                'struct': {
                    'name': 'FooAction_output',
                    'bases': ['Foo'],
                    'members': [
                        {'name': 'c', 'type': {'builtin': 'bool'}}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_action_output_non_struct(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action FooAction
    output (Foo)
        #- will not error
        float a

enum Foo
    A
    B

struct MyStruct
    int a

action BarAction
    output (Foo, MyStruct)

union MyUnion

action BonkAction
    output (MyStruct, MyUnion)
        float a

typedef string{} MyDict

action MyDictAction
    output (MyDict)
        #- will not error
        int a
''')
        expected_errors = [
            ":2: error: Invalid struct base type 'Foo'",
            ":14: error: Invalid struct base type 'Foo'",
            ":19: error: Invalid struct base type 'MyUnion'",
            ":20: error: Redefinition of 'BonkAction_output' member 'a'",
            ":25: error: Invalid struct base type 'MyDict'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_action_errors_enum(self):
        parser = SchemaMarkdownParser()
        parser.parse_string('''\
action FooAction
    errors (Foo)
        C

enum Foo
    A
    B

enum Bonk
    C

typedef Bonk Bar

action BarAction
    errors (Foo, Bar)
        D
''')
        self.assertDictEqual(parser.types, {
            'Bar': {
                'typedef': {
                    'name': 'Bar',
                    'type': {'user': 'Bonk'}
                }
            },
            'BarAction': {
                'action': {
                    'name': 'BarAction',
                    'errors': 'BarAction_errors'
                }
            },
            'BarAction_errors': {
                'enum': {
                    'name': 'BarAction_errors',
                    'bases': ['Foo', 'Bar'],
                    'values': [
                        {'name': 'D'}
                    ]
                }
            },
            'Bonk': {
                'enum': {
                    'name': 'Bonk',
                    'values': [
                        {'name': 'C'}
                    ]
                }
            },
            'Foo': {
                'enum': {
                    'name': 'Foo',
                    'values': [
                        {'name': 'A'},
                        {'name': 'B'}
                    ]
                }
            },
            'FooAction': {
                'action': {
                    'errors': 'FooAction_errors',
                    'name': 'FooAction'
                }
            },
            'FooAction_errors': {
                'enum': {
                    'name': 'FooAction_errors',
                    'bases': ['Foo'],
                    'values': [
                        {'name': 'C'}
                    ]
                }
            }
        })
        self.assertListEqual(parser.errors, [])

    def test_action_errors_non_enum(self):
        parser = SchemaMarkdownParser()
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.parse_string('''\
action FooAction
    errors (Foo)

struct Foo

struct Bonk

typedef Bonk Bar

enum MyEnum
    A

action BarAction
    errors (MyEnum, Bar)
        A

action BonkAction
    errors (MyEnum)
        A
''')
        expected_errors = [
            ":2: error: Invalid enum base type 'Foo'",
            ":14: error: Invalid enum base type 'Bar'",
            ":15: error: Redefinition of 'BarAction_errors' value 'A'",
            ":19: error: Redefinition of 'BonkAction_errors' value 'A'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)

    def test_finalize_no_parse(self):
        types = {
            'MyAction': {
                'action': {
                    'name': 'MyAction',
                    'query': 'MyAction_query'
                }
            },
            'MyAction_query': {
                'struct': {
                    'name': 'MyAction_query',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}}
                    ]
                }
            },
            'OtherType': {}
        }
        parser = SchemaMarkdownParser(types=types)
        parser.finalize()
        self.assertIs(parser.types, types)

    def test_finalize_no_parse_error(self):
        types = {
            'MyAction': {
                'action': {
                    'name': 'MyAction',
                    'query': 'MyAction_query',
                    'input': 'PositiveInt',
                    'output': 'MyAction_output'
                }
            },
            'MyAction_input': {
                'struct': {
                    'name': 'MyAction_input',
                    'members': [
                        {'name': 'a', 'type': {'user': 'NegativeInt'}},
                        {'name': 'a', 'type': {'builtin': 'int'}}
                    ]
                }
            },
            'PositiveInt': {
                'typedef': {
                    'name': 'PositiveInt',
                    'type': {'builtin': 'int'},
                    'attr': {'gt': 0}
                }
            }
        }
        parser = SchemaMarkdownParser(types=types)
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parser.finalize()
        expected_errors = [
            ":1: error: Redefinition of 'MyAction_input' member 'a'",
            ":1: error: Unknown type 'MyAction_output' from 'MyAction'",
            ":1: error: Unknown type 'MyAction_query' from 'MyAction'",
            ":1: error: Unknown type 'NegativeInt' from 'MyAction_input' member 'a'"
        ]
        self.assertListEqual(cm_exc.exception.errors, expected_errors)
        self.assertListEqual(parser.errors, expected_errors)
