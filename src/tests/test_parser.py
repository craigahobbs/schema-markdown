# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/main/LICENSE

# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring

import unittest

from schema_markdown import SchemaMarkdownParserError, parse_schema_markdown, validate_type_model


class TestParseSchemaMarkdown(unittest.TestCase):

    def test_simple(self):
        types = parse_schema_markdown('''\
# This is an enum
enum MyEnum
    Foo
    "Foo and Bar"
    ""
    "@#$!@"

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
    optional any l
    optional object m

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
        self.assertDictEqual(types, {
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
                        {'name': 'Foo and Bar'},
                        {'name': ''},
                        {'name': '@#$!@'}
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
                        {'name': 'l', 'optional': True, 'type': {'builtin': 'any'}},
                        {'name': 'm', 'optional': True, 'type': {'builtin': 'any'}}
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

    def test_array(self):
        types = parse_schema_markdown([
            'struct MyStruct',
            '    int a',
            '    int b'
        ])
        self.assertDictEqual(types, {
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

    def test_action_urls(self):
        types = parse_schema_markdown('''\
action MyAction

action MyActionUrl
    urls
        GET
        GET /
        *
        * /star
''')
        self.assertDictEqual(types, {
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

    def test_action_url_duplicate(self):
        errors = [
            ':4: error: Duplicate URL: GET /',
            ':7: error: Duplicate URL: GET',
            ':8: error: Redefinition of action urls'
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_action_url_typed(self):
        errors = [
            ':2: error: Syntax error',
            ':3: error: Syntax error'
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
action MyAction
    url (BaseType)
        GET /
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_group(self):
        types = parse_schema_markdown('''\
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
        self.assertDictEqual(types, {
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

    def test_struct_base_types(self):
        types = parse_schema_markdown('''\
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
        validate_type_model(types)
        self.assertDictEqual(types, {
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

    def test_struct_base_types_error(self):
        errors = [
            ":1: error: Invalid struct base type 'MyEnum'",
            ":8: error: Redefinition of 'MyStruct3' member 'a'",
            ":15: error: Invalid struct base type 'MyDict'",
            ":16: error: Redefinition of 'MyStruct5' member 'b'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_struct_base_types_circular(self):
        errors = [
            ":1: error: Circular base type detected for type 'MyStruct'",
            ":4: error: Circular base type detected for type 'MyStruct2'",
            ":7: error: Circular base type detected for type 'MyStruct3'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct (MyStruct2)
    int a

struct MyStruct2 (MyStruct3)
    int b

struct MyStruct3 (MyStruct)
    int c
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_enum_base_types(self):
        types = parse_schema_markdown('''\
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
        self.assertDictEqual(types, {
            'MyEnum': {'enum': {'bases': ['MyEnum2'], 'name': 'MyEnum', 'values': [{'name': 'c'}]}},
            'MyEnum2': {'enum': {'bases': ['MyEnum3'], 'name': 'MyEnum2', 'values': [{'name': 'b'}]}},
            'MyEnum3': {'enum': {'name': 'MyEnum3', 'values': [{'name': 'a'}]}},
            'MyEnum4': {'enum': {'name': 'MyEnum4', 'values': [{'name': 'd'}]}},
            'MyEnum5': {'enum': {'bases': ['MyEnum2', 'MyTypedef'], 'name': 'MyEnum5', 'values': [{'name': 'e'}]}},
            'MyTypedef': {'typedef': {'name': 'MyTypedef', 'type': {'user': 'MyEnum4'}}}
        })

    def test_enum_base_types_error(self):
        errors = [
            ":1: error: Invalid enum base type 'MyStruct'",
            ":8: error: Redefinition of 'MyEnum3' value 'A'",
            ":15: error: Invalid enum base type 'MyDict'",
            ":16: error: Redefinition of 'MyEnum5' value 'B'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_enum_base_types_circular(self):
        errors = [
            ":1: error: Circular base type detected for type 'MyEnum'",
            ":4: error: Circular base type detected for type 'MyEnum2'",
            ":7: error: Circular base type detected for type 'MyEnum3'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
enum MyEnum (MyEnum2)
    a

enum MyEnum2 (MyEnum3)
    b

enum MyEnum3 (MyEnum)
    c
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_multiple(self):
        types = parse_schema_markdown('''\
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
''', validate=False)
        parse_schema_markdown('''\
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
''', types=types)
        self.assertDictEqual(types, {
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

    def test_error_multiple(self):
        errors = [
            ":1: error: Invalid struct base type 'MyStruct2'"
        ]
        types = parse_schema_markdown('''\
struct MyStruct (MyStruct2)
    int a
''', validate=False)
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct3
    int b
''', types=types)
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_array_attr(self):
        types = parse_schema_markdown('''\
struct MyStruct
    MyStruct2[len > 0] a
struct MyStruct2
''')
        self.assertDictEqual(types, {
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

    def test_dict_attr(self):
        types = parse_schema_markdown('''\
struct MyStruct
    MyEnum : MyStruct2{len > 0} a
enum MyEnum
struct MyStruct2
''')
        self.assertDictEqual(types, {
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

    def test_nullable(self):
        types = parse_schema_markdown('''\
struct MyStruct
    int(nullable) a
    float[nullable] b
    float(nullable)[nullable] c
    bool{nullable} d
    bool(nullable){nullable} e
    string(nullable) : date{} f

typedef string(nullable) MyTypedef
''')
        self.assertDictEqual(types, {
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

    def test_nullable_with_attr(self):
        types = parse_schema_markdown('''\
struct MyStruct
    int(nullable, > 0) a
''')
        self.assertDictEqual(types, {
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {'name': 'a', 'type': {'builtin': 'int'}, 'attr': {'gt': 0.0, 'nullable': True}}
                    ]
                }
            }
        })

    def test_invalid_attr(self):
        errors = [
            ":2: error: Invalid attribute 'len > 0' from 'MyStruct' member 'a'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    MyStruct2(len > 0) a
struct MyStruct2
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_unknown_type(self):
        errors = [
            "foo:2: error: Unknown type 'MyBadType' from 'Foo' member 'a'",
            "foo:6: error: Unknown type 'MyBadType2' from 'MyAction_input' member 'a'",
            "foo:8: error: Unknown type 'MyBadType' from 'MyAction_output' member 'b'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct Foo
    MyBadType a

action MyAction
    input
        MyBadType2 a
    output
        MyBadType b
''', filename='foo')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_unknown_array_type(self):
        errors = [
            "foo:2: error: Unknown type 'MyBadType' from 'MyStruct' member 'a'",
            "foo:3: error: Unknown type 'MyBadType' from 'MyStruct' member 'b'",
            "foo:5: error: Unknown type 'MyBadType' from 'MyTypedef'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    MyBadType[] a
    MyTypedef[] b

typedef MyBadType MyTypedef
''', filename='foo')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_unknown_dict_type(self):
        errors = [
            "foo:2: error: Unknown type 'MyBadType' from 'MyStruct' member 'a'",
            "foo:3: error: Unknown type 'MyBadType' from 'MyStruct' member 'b'",
            "foo:5: error: Unknown type 'MyBadType' from 'MyTypedef'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    MyBadType{} a
    MyTypedef{} b

typedef MyBadType MyTypedef
''', filename='foo')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_unknown_dict_key_type(self):
        errors = [
            "foo:2: error: Invalid dictionary key type from 'MyStruct' member 'a'",
            "foo:2: error: Unknown type 'MyBadType' from 'MyStruct' member 'a'",
            "foo:3: error: Invalid dictionary key type from 'MyStruct' member 'b'",
            "foo:3: error: Unknown type 'MyBadType' from 'MyStruct' member 'b'",
            "foo:5: error: Unknown type 'MyBadType' from 'MyTypedef'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    MyBadType : int{} a
    MyTypedef : int{} b

typedef MyBadType MyTypedef
''', filename='foo')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_action_type(self):
        errors = [
            "foo:2: error: Invalid reference to action 'MyAction' from 'Foo' member 'a'",
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct Foo
    MyAction a

action MyAction
''', filename='foo')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_struct_redefinition(self):
        errors = [
            ":4: error: Redefinition of type 'Foo'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct Foo
    int a

enum Foo
    A
    B
''')
        self.assertEqual(str(cm_exc.exception), ":4: error: Redefinition of type 'Foo'")
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_enum_redefinition(self):
        errors = [
            ":5: error: Redefinition of type 'Foo'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
enum Foo
    A
    B

struct Foo
    int a
''')
        self.assertEqual(str(cm_exc.exception), ":5: error: Redefinition of type 'Foo'")
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_typedef_redefinition(self):
        errors = [
            ":4: error: Redefinition of type 'Foo'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct Foo
    int a

typedef int(> 5) Foo
''')
        self.assertEqual(str(cm_exc.exception), ":4: error: Redefinition of type 'Foo'")
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_action_redefinition(self):
        errors = [
            ":5: error: Redefinition of action 'MyAction'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
action MyAction
    input
        int a

action MyAction
    input
        string b
''')
        self.assertEqual(str(cm_exc.exception), ":5: error: Redefinition of action 'MyAction'")
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_action_section(self):
        errors = [
            ':6: error: Syntax error',
            ':7: error: Syntax error',
            ':8: error: Syntax error',
            ':10: error: Syntax error',
            ':11: error: Syntax error',
            ':12: error: Syntax error'
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_member(self):
        errors = [
            ':2: error: Syntax error',
            ':8: error: Syntax error',
            ':10: error: Syntax error'
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_enum(self):
        errors = [
            ':2: error: Syntax error',
            ':3: error: Syntax error',
            ':4: error: Syntax error',
            ':8: error: Syntax error',
            ':12: error: Syntax error'
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_attributes(self):
        types = parse_schema_markdown('''\
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
        self.assertDictEqual(types, {
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

    def test_error_attribute_eq(self):
        errors = [
            ":2: error: Invalid attribute '== 7' from 'MyStruct' member 's'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    string(== 7) s
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_attribute_lt(self):
        errors = [
            ":2: error: Invalid attribute '< 7' from 'MyStruct' member 's'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    string(< 7) s
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_attribute_gt(self):
        errors = [
            ":2: error: Invalid attribute '> 7' from 'MyStruct' member 's'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    string(> 7) s
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_attribute_lt_gt(self):
        errors = [
            ":2: error: Invalid attribute '< 7' from 'MyStruct' member 's'",
            ":2: error: Invalid attribute '> 7' from 'MyStruct' member 's'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    string(< 7, > 7) s
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_attribute_lte_gte(self):
        errors = [
            ":6: error: Invalid attribute '>= 1' from 'MyStruct' member 'a'",
            ":7: error: Invalid attribute '<= 2' from 'MyStruct' member 'b'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
enum MyEnum
    Foo
    Bar

struct MyStruct
    MyStruct(>= 1) a
    MyEnum(<= 2) b
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_attribute_len_eq(self):
        errors = [
            ":2: error: Invalid attribute 'len == 1' from 'MyStruct' member 'i'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    int(len == 1) i
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_attribute_len_lt(self):
        errors = [
            ":2: error: Invalid attribute 'len < 10' from 'MyStruct' member 'f'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    float(len < 10) f
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_attribute_len_gt(self):
        errors = [
            ":2: error: Invalid attribute 'len > 1' from 'MyStruct' member 'i'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    int(len > 1) i
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_attribute_len_lt_gt(self):
        errors = [
            ":2: error: Invalid attribute 'len < 10' from 'MyStruct' member 'f'",
            ":2: error: Invalid attribute 'len > 10' from 'MyStruct' member 'f'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    float(len < 10, len > 10) f
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_attribute_len_lte_gte(self):
        errors = [
            ":2: error: Invalid attribute 'len <= 10' from 'MyStruct' member 'f'",
            ":3: error: Invalid attribute 'len >= 10' from 'MyStruct' member 'f2'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    float(len <= 10) f
    float(len >= 10) f2
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_attribute_invalid(self):
        errors = [
            ':2: error: Syntax error'
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    string(regex="abc") a
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_member_invalid(self):
        errors = [
            ':1: error: Syntax error',
            ':5: error: Syntax error'
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
    string a

enum MyEnum
    Foo
    int b
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_member_redefinition(self):
        errors = [
            ":4: error: Redefinition of 'MyStruct' member 'b'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct MyStruct
    string b
    int a
    float b
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_enum_duplicate_value(self):
        errors = [
            ":4: error: Redefinition of 'MyEnum' value 'bar'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
enum MyEnum
    bar
    foo
    bar
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_doc(self):
        types = parse_schema_markdown('''\
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
        self.assertDictEqual(types, {
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

    def test_typedef(self):
        types = parse_schema_markdown('''\
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
        self.assertDictEqual(types, {
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

    def test_error_dict_non_string_key(self):
        errors = [
            ":2: error: Invalid dictionary key type from 'Foo' member 'a'",
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
struct Foo
    int : int {} a
''')
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_action_section_redefinition(self):
        errors = [
            ':13: error: Redefinition of action urls',
            ':15: error: Redefinition of action path',
            ':17: error: Redefinition of action query',
            ':19: error: Redefinition of action input',
            ':21: error: Redefinition of action output'
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_error_action_input_member_redefinition(self):
        errors = [
            ":3: error: Redefinition of 'MyAction_path' member 'a'",
            ":4: error: Redefinition of 'MyAction_path' member 'b'",
            ":6: error: Redefinition of 'MyAction_query' member 'a'",
            ":8: error: Redefinition of 'MyAction_input' member 'b'",
            ":11: error: Redefinition of 'MyAction2_path' member 'a'",
            ":11: error: Redefinition of 'MyAction2_path' member 'b'",
            ":13: error: Redefinition of 'MyAction2_query' member 'a'",
            ":15: error: Redefinition of 'MyAction2_input' member 'b'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_action_path_base_types(self):
        types = parse_schema_markdown('''\
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
        self.assertDictEqual(types, {
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

    def test_action_path_non_struct(self):
        errors = [
            ":2: error: Invalid struct base type 'Foo'",
            ":14: error: Invalid struct base type 'Foo'",
            ":19: error: Invalid struct base type 'MyUnion'",
            ":20: error: Redefinition of 'BonkAction_path' member 'a'",
            ":25: error: Invalid struct base type 'MyDict'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_action_query_base_types(self):
        types = parse_schema_markdown('''\
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
        self.assertDictEqual(types, {
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

    def test_action_query_non_struct(self):
        errors = [
            ":2: error: Invalid struct base type 'Foo'",
            ":14: error: Invalid struct base type 'Foo'",
            ":19: error: Invalid struct base type 'MyUnion'",
            ":20: error: Redefinition of 'BonkAction_query' member 'a'",
            ":25: error: Invalid struct base type 'MyDict'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_action_input_base_types(self):
        types = parse_schema_markdown('''\
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
        self.assertDictEqual(types, {
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

    def test_action_input_non_struct(self):
        errors = [
            ":2: error: Invalid struct base type 'Foo'",
            ":14: error: Invalid struct base type 'Foo'",
            ":19: error: Invalid struct base type 'MyUnion'",
            ":20: error: Redefinition of 'BonkAction_input' member 'a'",
            ":25: error: Invalid struct base type 'MyDict'",
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_action_input_member_redef(self):
        errors = [
            ":2: error: Invalid struct base type 'Foo'",
            ":14: error: Invalid struct base type 'Foo'",
            ":19: error: Invalid struct base type 'MyUnion'",
            ":20: error: Redefinition of 'BonkAction_input' member 'a'",
            ":25: error: Invalid struct base type 'MyDict'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_action_output_struct(self):
        types = parse_schema_markdown('''\
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
        self.assertDictEqual(types, {
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

    def test_action_output_non_struct(self):
        errors = [
            ":2: error: Invalid struct base type 'Foo'",
            ":14: error: Invalid struct base type 'Foo'",
            ":19: error: Invalid struct base type 'MyUnion'",
            ":20: error: Redefinition of 'BonkAction_output' member 'a'",
            ":25: error: Invalid struct base type 'MyDict'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)

    def test_action_errors_enum(self):
        types = parse_schema_markdown('''\
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
        self.assertDictEqual(types, {
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

    def test_action_errors_non_enum(self):
        errors = [
            ":2: error: Invalid enum base type 'Foo'",
            ":14: error: Invalid enum base type 'Bar'",
            ":15: error: Redefinition of 'BarAction_errors' value 'A'",
            ":19: error: Redefinition of 'BonkAction_errors' value 'A'"
        ]
        with self.assertRaises(SchemaMarkdownParserError) as cm_exc:
            parse_schema_markdown('''\
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
        self.assertEqual(str(cm_exc.exception), '\n'.join(errors))
        self.assertListEqual(cm_exc.exception.errors, errors)
