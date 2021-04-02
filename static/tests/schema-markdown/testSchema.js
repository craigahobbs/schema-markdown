// Licensed under the MIT License
// https://github.com/craigahobbs/schema-markdown/blob/master/LICENSE

/* eslint-disable id-length */

import {getReferencedTypes, validateType, validateTypeModel, validateTypeModelTypes} from '../../src/schema-markdown/schema.js';
import test from 'ava';
import {typeModel} from '../../src/schema-markdown/typeModel.js';


//
// getReferencedTypes tests
//

test('getReferencedTypes', (t) => {
    const types = {
        'MyAction': {
            'action': {
                'name': 'MyAction',
                'path': 'MyAction_path',
                'query': 'MyAction_query',
                'input': 'MyAction_input',
                'output': 'MyAction_output',
                'errors': 'MyAction_errors'
            }
        },
        'MyAction_path': {
            'struct': {
                'name': 'MyAction_path',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'string'}}
                ]
            }
        },
        'MyAction_query': {
            'struct': {
                'name': 'MyAction_query',
                'members': [
                    {'name': 'b', 'type': {'array': {'type': {'user': 'MyEnum'}}}}
                ]
            }
        },
        'MyAction_input': {
            'struct': {
                'name': 'MyAction_input',
                'members': [
                    {'name': 'c', 'type': {'dict': {'type': {'user': 'MyStruct'}}}}
                ]
            }
        },
        'MyAction_output': {
            'struct': {
                'name': 'MyAction_output',
                'members': [
                    {'name': 'd', 'type': {'dict': {'type': {'builtin': 'int'}, 'keyType': {'user': 'MyEnum2'}}}}
                ]
            }
        },
        'MyAction_errors': {
            'enum': {
                'name': 'MyAction_errors',
                'values': [
                    {'name': 'A'}
                ]
            }
        },
        'MyEnum': {'enum': {'name': 'MyEnum'}},
        'MyEnum2': {'enum': {'name': 'MyEnum2'}},
        'MyEnumNoref': {'enum': {'name': 'MyEnumNoref'}},
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'user': 'MyTypedef'}},
                    {'name': 'b', 'type': {'user': 'MyStructEmpty'}}
                ]
            }
        },
        'MyStructEmpty': {'struct': {'name': 'MyStructEmpty'}},
        'MyStructNoref': {'struct': {'name': 'MyStructNoref'}},
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'user': 'MyTypedef2'}
            }
        },
        'MyTypedef2': {
            'typedef': {
                'name': 'MyTypedef2',
                'type': {'builtin': 'int'}
            }
        },
        'MyTypedefNoref': {
            'typedef': {
                'name': 'MyTypedefNoref',
                'type': {'builtin': 'int'}
            }
        }
    };

    const expectedTypes = validateTypeModelTypes(types);
    delete expectedTypes.MyEnumNoref;
    delete expectedTypes.MyStructNoref;
    delete expectedTypes.MyTypedefNoref;

    const referencedTypes = getReferencedTypes(types, 'MyAction');
    validateTypeModelTypes(referencedTypes);
    t.deepEqual(referencedTypes, expectedTypes);
});


test('getReferencedTypes, empty action', (t) => {
    const types = {
        'MyAction': {
            'action': {
                'name': 'MyAction'
            }
        },
        'MyTypedefNoref': {
            'typedef': {
                'name': 'MyTypedefNoref',
                'type': {'builtin': 'int'}
            }
        }
    };

    const expectedTypes = validateTypeModelTypes(types);
    delete expectedTypes.MyTypedefNoref;

    const referencedTypes = getReferencedTypes(types, 'MyAction');
    validateTypeModelTypes(referencedTypes);
    t.deepEqual(referencedTypes, expectedTypes);
});


test('getReferencedTypes, circular', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'user': 'MyStruct2'}}
                ]
            }
        },
        'MyStruct2': {
            'struct': {
                'name': 'MyStruct2',
                'members': [
                    {'name': 'a', 'type': {'user': 'MyStruct'}}
                ]
            }
        },
        'MyTypedefNoref': {
            'typedef': {
                'name': 'MyTypedefNoref',
                'type': {'builtin': 'int'}
            }
        }
    };

    const expectedTypes = validateTypeModelTypes(types);
    delete expectedTypes.MyTypedefNoref;

    const referencedTypes = getReferencedTypes(types, 'MyStruct');
    validateTypeModelTypes(referencedTypes);
    t.deepEqual(referencedTypes, expectedTypes);
});


test('getReferencedTypes, struct base', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'bases': ['MyStruct2'],
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}}
                ]
            }
        },
        'MyStruct2': {
            'struct': {
                'name': 'MyStruct2',
                'members': [
                    {'name': 'b', 'type': {'user': 'MyTypedef'}}
                ]
            }
        },
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'builtin': 'int'}
            }
        },
        'MyTypedefNoref': {
            'typedef': {
                'name': 'MyTypedefNoref',
                'type': {'builtin': 'int'}
            }
        }
    };

    const expectedTypes = validateTypeModelTypes(types);
    delete expectedTypes.MyTypedefNoref;

    const referencedTypes = getReferencedTypes(types, 'MyStruct');
    validateTypeModelTypes(referencedTypes);
    t.deepEqual(referencedTypes, expectedTypes);
});


test('getReferencedTypes, enum base', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum',
                'bases': ['MyEnum2'],
                'values': [
                    {'name': 'a'}
                ]
            }
        },
        'MyEnum2': {
            'enum': {
                'name': 'MyEnum2',
                'values': [
                    {'name': 'b'}
                ]
            }
        },
        'MyTypedefNoref': {
            'typedef': {
                'name': 'MyTypedefNoref',
                'type': {'builtin': 'int'}
            }
        }
    };

    const expectedTypes = validateTypeModelTypes(types);
    delete expectedTypes.MyTypedefNoref;

    const referencedTypes = getReferencedTypes(types, 'MyEnum');
    validateTypeModelTypes(referencedTypes);
    t.deepEqual(referencedTypes, expectedTypes);
});


//
// validateType tests
//

function validateTypeHelper(type, obj) {
    const types = {
        'MyTypedef': {
            'typedef': {
                'type': type
            }
        }
    };
    return validateType(types, 'MyTypedef', obj);
}


test('validateType, unknown', (t) => {
    let errorMessage = null;
    try {
        validateType({}, 'Unknown', null);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Unknown type 'Unknown'");
});


test('validateType, string', (t) => {
    const obj = 'abc';
    t.is(validateTypeHelper({'builtin': 'string'}, obj), obj);
});


test('validateType, string error', (t) => {
    let errorMessage = null;
    const obj = 7;
    try {
        validateTypeHelper({'builtin': 'string'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 7 (type 'number'), expected type 'string'");
});


test('validateType, string error undefined', (t) => {
    let errorMessage = null;
    const obj = undefined;
    try {
        validateTypeHelper({'builtin': 'string'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value undefined (type 'undefined'), expected type 'string'");
});


test('validateType, int', (t) => {
    const obj = 7;
    t.is(validateTypeHelper({'builtin': 'int'}, obj), obj);
});


test('validateType, int string', (t) => {
    const obj = '7';
    t.is(validateTypeHelper({'builtin': 'int'}, obj), 7);
});


test('validateType, int float', (t) => {
    let errorMessage = null;
    const obj = 7.1;
    try {
        validateTypeHelper({'builtin': 'int'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 7.1 (type 'number'), expected type 'int'");
});


test('validateType, int error', (t) => {
    let errorMessage = null;
    const obj = 'abc';
    try {
        validateTypeHelper({'builtin': 'int'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'int'");
});


test('validateType, int error float', (t) => {
    let errorMessage = null;
    const obj = 7.5;
    try {
        validateTypeHelper({'builtin': 'int'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 7.5 (type 'number'), expected type 'int'");
});


test('validateType, int error bool', (t) => {
    let errorMessage = null;
    const obj = true;
    try {
        validateTypeHelper({'builtin': 'int'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value true (type 'boolean'), expected type 'int'");
});


test('validateType, float', (t) => {
    const obj = 7.5;
    t.is(validateTypeHelper({'builtin': 'float'}, obj), obj);
});


test('validateType, float int', (t) => {
    const obj = 7;
    t.is(validateTypeHelper({'builtin': 'float'}, obj), 7.0);
});


test('validateType, float string', (t) => {
    const obj = '7.5';
    t.is(validateTypeHelper({'builtin': 'float'}, obj), 7.5);
});


test('validateType, float error', (t) => {
    let errorMessage = null;
    const obj = 'abc';
    try {
        validateTypeHelper({'builtin': 'float'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'float'");
});


test('validateType, float error nan', (t) => {
    let errorMessage = null;
    const obj = 'nan';
    try {
        validateTypeHelper({'builtin': 'float'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"nan\" (type 'string'), expected type 'float'");
});


test('validateType, float error inf', (t) => {
    let errorMessage = null;
    const obj = 'inf';
    try {
        validateTypeHelper({'builtin': 'float'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"inf\" (type 'string'), expected type 'float'");
});


test('validateType, float error bool', (t) => {
    let errorMessage = null;
    const obj = true;
    try {
        validateTypeHelper({'builtin': 'float'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value true (type 'boolean'), expected type 'float'");
});


test('validateType, bool', (t) => {
    const obj = false;
    t.is(validateTypeHelper({'builtin': 'bool'}, obj), obj);
});


test('validateType, bool true', (t) => {
    const obj = 'true';
    t.is(validateTypeHelper({'builtin': 'bool'}, obj), true);
});


test('validateType, bool false', (t) => {
    const obj = 'false';
    t.is(validateTypeHelper({'builtin': 'bool'}, obj), false);
});


test('validateType, bool error', (t) => {
    let errorMessage = null;
    const obj = 0;
    try {
        validateTypeHelper({'builtin': 'bool'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 0 (type 'number'), expected type 'bool'");
});


test('validateType, bool error string', (t) => {
    let errorMessage = null;
    const obj = 'abc';
    try {
        validateTypeHelper({'builtin': 'bool'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'bool'");
});


test('validateType, date', (t) => {
    const obj = new Date(Date.UTC(2020, 5, 26));
    t.deepEqual(validateTypeHelper({'builtin': 'date'}, obj), new Date(2020, 5, 26));
});


test('validateType, date datetime', (t) => {
    const obj = new Date(Date.UTC(2020, 5, 26, 18, 8));
    t.deepEqual(validateTypeHelper({'builtin': 'date'}, obj), new Date(2020, 5, 26));
});


test('validateType, date string', (t) => {
    const obj = '2020-06-26';
    t.deepEqual(validateTypeHelper({'builtin': 'date'}, obj), new Date(2020, 5, 26));
});


test('validateType, date string datetime', (t) => {
    const obj = '2020-06-26T13:11:00-07:00';
    t.deepEqual(validateTypeHelper({'builtin': 'date'}, obj), new Date(2020, 5, 26));
});


test('validateType, date string error', (t) => {
    let errorMessage = null;
    const obj = 'abc';
    try {
        validateTypeHelper({'builtin': 'date'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'date'");
});


test('validateType, date error', (t) => {
    let errorMessage = null;
    const obj = 0;
    try {
        validateTypeHelper({'builtin': 'date'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 0 (type 'number'), expected type 'date'");
});


test('validateType, date error excluded', (t) => {
    let errorMessage = null;
    const obj = 'December 17, 1995 03:24:00';
    try {
        validateTypeHelper({'builtin': 'date'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"December 17, 1995 03:24:00\" (type 'string'), expected type 'date'");
});


test('validateType, datetime', (t) => {
    const obj = new Date(2020, 5, 26, 18, 8);
    t.deepEqual(validateTypeHelper({'builtin': 'datetime'}, obj), obj);
});


test('validateType, datetime date', (t) => {
    const obj = new Date(2020, 5, 26);
    t.deepEqual(validateTypeHelper({'builtin': 'datetime'}, obj), obj);
});


test('validateType, datetime string', (t) => {
    const obj = '2020-06-26T13:11:00-07:00';
    t.deepEqual(validateTypeHelper({'builtin': 'datetime'}, obj), new Date(Date.UTC(2020, 5, 26, 20, 11)));
});


test('validateType, datetime string date', (t) => {
    const obj = '2020-06-26';
    t.deepEqual(validateTypeHelper({'builtin': 'datetime'}, obj), new Date(Date.UTC(2020, 5, 26)));
});


test('validateType, datetime string error', (t) => {
    let errorMessage = null;
    const obj = 'abc';
    try {
        validateTypeHelper({'builtin': 'datetime'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'datetime'");
});


test('validateType, datetime error', (t) => {
    let errorMessage = null;
    const obj = 0;
    try {
        validateTypeHelper({'builtin': 'datetime'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 0 (type 'number'), expected type 'datetime'");
});


test('validateType, datetime error excluded', (t) => {
    let errorMessage = null;
    const obj = 'December 17, 1995 03:24:00';
    try {
        validateTypeHelper({'builtin': 'datetime'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"December 17, 1995 03:24:00\" (type 'string'), expected type 'datetime'");
});


test('validateType, uuid', (t) => {
    const obj = 'AED91C7B-DCFD-49B3-A483-DBC9EA2031A3';
    t.deepEqual(validateTypeHelper({'builtin': 'uuid'}, obj), obj);
});


test('validateType, uuid lowercase', (t) => {
    const obj = 'aed91c7b-dcfd-49b3-a483-dbc9ea2031a3';
    t.deepEqual(validateTypeHelper({'builtin': 'uuid'}, obj), obj);
});


test('validateType, uuid error', (t) => {
    let errorMessage = null;
    const obj = 0;
    try {
        validateTypeHelper({'builtin': 'uuid'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 0 (type 'number'), expected type 'uuid'");
});


test('validateType, uuid error string', (t) => {
    let errorMessage = null;
    const obj = 'abc';
    try {
        validateTypeHelper({'builtin': 'uuid'}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'uuid'");
});


test('validateType, object', (t) => {
    const obj = {};
    t.deepEqual(validateTypeHelper({'builtin': 'object'}, obj), obj);
});


test('validateType, object string', (t) => {
    const obj = 'abc';
    t.deepEqual(validateTypeHelper({'builtin': 'object'}, obj), obj);
});


test('validateType, object int', (t) => {
    const obj = 7;
    t.deepEqual(validateTypeHelper({'builtin': 'object'}, obj), obj);
});


test('validateType, object bool', (t) => {
    const obj = true;
    t.deepEqual(validateTypeHelper({'builtin': 'object'}, obj), obj);
});


test('validateType, array', (t) => {
    const obj = [1, 2, 3];
    t.deepEqual(validateTypeHelper({'array': {'type': {'builtin': 'int'}}}, obj), obj);
});


test('validateType, array nullable', (t) => {
    const obj = [1, null, 3];
    t.deepEqual(validateTypeHelper({'array': {'type': {'builtin': 'int'}, 'attr': {'nullable': true}}}, obj), obj);

    let errorMessage = null;
    try {
        validateTypeHelper({'array': {'type': {'builtin': 'int'}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value null (type 'object') for member '1', expected type 'int'");
});


test('validateType, array nullable as string', (t) => {
    const obj = ['1', 'null', '3'];
    t.deepEqual(
        validateTypeHelper({'array': {'type': {'builtin': 'int'}, 'attr': {'nullable': true}}}, obj),
        [1, null, 3]
    );

    let errorMessage = null;
    try {
        validateTypeHelper({'array': {'type': {'builtin': 'int'}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"null\" (type 'string') for member '1', expected type 'int'");
});


test('validateType, array empty string', (t) => {
    const obj = '';
    t.deepEqual(validateTypeHelper({'array': {'type': {'builtin': 'int'}}}, obj), []);
});


test('validateType, array attributes', (t) => {
    const obj = [1, 2, 3];
    t.deepEqual(validateTypeHelper({'array': {'type': {'builtin': 'int'}, 'attr': {'lt': 5}}}, obj), obj);
});


test('validateType, array error', (t) => {
    let errorMessage = null;
    const obj = 'abc';
    try {
        validateTypeHelper({'array': {'type': {'builtin': 'int'}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'array'");
});


test('validateType, array error value', (t) => {
    let errorMessage = null;
    const obj = [1, 'abc', 3];
    try {
        validateTypeHelper({'array': {'type': {'builtin': 'int'}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string') for member '1', expected type 'int'");
});


test('validateType, array error value nested', (t) => {
    let errorMessage = null;
    const obj = [[1, 2], [1, 'abc', 3]];
    try {
        validateTypeHelper({'array': {'type': {'array': {'type': {'builtin': 'int'}}}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string') for member '1.1', expected type 'int'");
});


test('validateType, array attribute error', (t) => {
    let errorMessage = null;
    const obj = [1, 2, 5];
    try {
        validateTypeHelper({'array': {'type': {'builtin': 'int'}, 'attr': {'lt': 5}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 5 (type 'number') for member '2', expected type 'int' [< 5]");
});


test('validateType, dict', (t) => {
    const obj = {'a': 1, 'b': 2, 'c': 3};
    t.deepEqual(validateTypeHelper({'dict': {'type': {'builtin': 'int'}}}, obj), obj);
});


test('validateType, dict nullable', (t) => {
    const obj = {'a': 1, 'b': null, 'c': 3};
    t.deepEqual(validateTypeHelper({'dict': {'type': {'builtin': 'int'}, 'attr': {'nullable': true}}}, obj), obj);

    let errorMessage = null;
    try {
        validateTypeHelper({'dict': {'type': {'builtin': 'int'}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value null (type 'object') for member 'b', expected type 'int'");
});


test('validateType, dict nullable as string', (t) => {
    const obj = {'a': '1', 'b': 'null', 'c': '3'};
    t.deepEqual(
        validateTypeHelper({'dict': {'type': {'builtin': 'int'}, 'attr': {'nullable': true}}}, obj),
        {'a': 1, 'b': null, 'c': 3}
    );

    let errorMessage = null;
    try {
        validateTypeHelper({'dict': {'type': {'builtin': 'int'}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"null\" (type 'string') for member 'b', expected type 'int'");
});


test('validateType, dict key nullable', (t) => {
    const obj = new Map();
    obj.set('a', 1);
    obj.set(null, 2);
    obj.set('c', 3);
    const obj2 = validateTypeHelper({'dict': {'type': {'builtin': 'int'}, 'keyAttr': {'nullable': true}}}, obj);
    t.is(Array.from(obj2.keys()).length, 3);
    t.is(obj2.get('a'), 1);
    t.is(obj2.get(null), 2);
    t.is(obj2.get('c'), 3);

    let errorMessage = null;
    try {
        validateTypeHelper({'dict': {'type': {'builtin': 'int'}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value null (type 'object'), expected type 'string'");
});


test('validateType, dict key nullable as string', (t) => {
    const obj = new Map();
    obj.set('a', 1);
    obj.set(null, 2);
    obj.set('c', 3);
    const obj2 = validateTypeHelper({'dict': {'type': {'builtin': 'int'}, 'keyAttr': {'nullable': true}}}, obj);
    t.is(Array.from(obj2.keys()).length, 3);
    t.is(obj2.get('a'), 1);
    t.is(obj2.get(null), 2);
    t.is(obj2.get('c'), 3);

    let errorMessage = null;
    try {
        validateTypeHelper({'dict': {'type': {'builtin': 'int'}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value null (type 'object'), expected type 'string'");
});


test('validateType, dict empty string', (t) => {
    const obj = '';
    t.deepEqual(validateTypeHelper({'dict': {'type': {'builtin': 'int'}}}, obj), {});
});


test('validateType, dict attributes', (t) => {
    const obj = {'a': 1, 'b': 2, 'c': 3};
    t.deepEqual(validateTypeHelper({'dict': {'type': {'builtin': 'int'}, 'attr': {'lt': 5}}}, obj), obj);
});


test('validateType, dict error', (t) => {
    let errorMessage = null;
    const obj = 'abc';
    try {
        validateTypeHelper({'dict': {'type': {'builtin': 'int'}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'dict'");
});


test('validateType, dict error value', (t) => {
    let errorMessage = null;
    const obj = {'a': 1, 'b': 'abc', 'c': 3};
    try {
        validateTypeHelper({'dict': {'type': {'builtin': 'int'}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string') for member 'b', expected type 'int'");
});


test('validateType, dict error value nested', (t) => {
    let errorMessage = null;
    const obj = [{'a': 1}, {'a': 1, 'b': 'abc', 'c': 3}];
    try {
        validateTypeHelper({'array': {'type': {'dict': {'type': {'builtin': 'int'}}}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string') for member '1.b', expected type 'int'");
});


test('validateType, dict attribute error', (t) => {
    let errorMessage = null;
    const obj = {'a': 1, 'b': 2, 'c': 5};
    try {
        validateTypeHelper({'dict': {'type': {'builtin': 'int'}, 'attr': {'lt': 5}}}, obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 5 (type 'number') for member 'c', expected type 'int' [< 5]");
});


test('validateType, dict key type', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum',
                'values': [
                    {'name': 'A'},
                    {'name': 'B'}
                ]
            }
        },
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'dict': {'type': {'builtin': 'int'}, 'keyType': {'user': 'MyEnum'}}}
            }
        }
    };
    let errorMessage = null;

    let obj = {'A': 1, 'B': 2};
    t.deepEqual(validateType(types, 'MyTypedef', obj), obj);

    obj = {'A': 1, 'C': 2};
    try {
        validateType(types, 'MyTypedef', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"C\" (type 'string'), expected type 'MyEnum'");
});


test('validateType, dict key attr', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'dict': {'type': {'builtin': 'int'}, 'keyType': {'builtin': 'string'}, 'keyAttr': {'lenLT': 10}}}
            }
        }
    };
    let errorMessage = null;

    let obj = {'abc': 1, 'abcdefghi': 2};
    t.deepEqual(validateType(types, 'MyTypedef', obj), obj);

    obj = {'abc': 1, 'abcdefghij': 2};
    try {
        validateType(types, 'MyTypedef', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abcdefghij\" (type 'string'), expected type 'string' [len < 10]");
});


test('validateType, enum', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum',
                'values': [
                    {'name': 'a'},
                    {'name': 'b'}
                ]
            }
        }
    };
    let errorMessage = null;

    let obj = 'a';
    t.is(validateType(types, 'MyEnum', obj), obj);

    obj = 'c';
    try {
        validateType(types, 'MyEnum', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"c\" (type 'string'), expected type 'MyEnum'");
});


test('validateType, enum empty', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum'
            }
        }
    };
    let errorMessage = null;

    const obj = 'a';
    try {
        validateType(types, 'MyEnum', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"a\" (type 'string'), expected type 'MyEnum'");
});


test('validateType, enum base', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum',
                'bases': ['MyEnum2'],
                'values': [
                    {'name': 'a'}
                ]
            }
        },
        'MyEnum2': {
            'enum': {
                'name': 'MyEnum2',
                'bases': ['MyTypedef']
            }
        },
        'MyEnum3': {
            'enum': {
                'name': 'MyEnum3',
                'values': [
                    {'name': 'b'}
                ]
            }
        },
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'user': 'MyEnum3'}
            }
        }
    };
    let errorMessage = null;

    let obj = 'a';
    t.is(validateType(types, 'MyEnum', obj), obj);

    obj = 'b';
    t.is(validateType(types, 'MyEnum', obj), obj);

    obj = 'c';
    try {
        validateType(types, 'MyEnum', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"c\" (type 'string'), expected type 'MyEnum'");
});


test('validateType, typedef', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'builtin': 'int'},
                'attr': {'gte': 5}
            }
        }
    };
    let errorMessage = null;

    let obj = 5;
    t.is(validateType(types, 'MyTypedef', obj), obj);

    obj = 4;
    try {
        validateType(types, 'MyTypedef', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 4 (type 'number'), expected type 'MyTypedef' [>= 5]");

    obj = null;
    try {
        validateType(types, 'MyTypedef', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value null (type 'object'), expected type 'MyTypedef'");

    obj = 'null';
    try {
        validateType(types, 'MyTypedef', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"null\" (type 'string'), expected type 'int'");
});


test('validateType, typedef no attr', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'builtin': 'int'}
            }
        }
    };
    const obj = 5;
    t.is(validateType(types, 'MyTypedef', obj), obj);
});


test('validateType, typedef type error', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'builtin': 'int'}
            }
        }
    };
    let errorMessage = null;

    const obj = 'abc';
    try {
        validateType(types, 'MyTypedef', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'int'");
});


test('validateType, typedef attr eq', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'builtin': 'int'},
                'attr': {'eq': 5}
            }
        }
    };
    let errorMessage = null;
    validateType(types, 'MyTypedef', 5);
    try {
        validateType(types, 'MyTypedef', 7);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 7 (type 'number'), expected type 'MyTypedef' [== 5]");
});


test('validateType, typedef attr nullable', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'builtin': 'int'},
                'attr': {'nullable': true}
            }
        }
    };
    let errorMessage = null;
    t.is(validateType(types, 'MyTypedef', 5), 5);
    t.is(validateType(types, 'MyTypedef', null), null);
    t.is(validateType(types, 'MyTypedef', 'null'), null);
    try {
        validateType(types, 'MyTypedef', 'abc');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'int'");
});


test('validateType, typedef attr lt', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'builtin': 'int'},
                'attr': {'lt': 5}
            }
        }
    };
    let errorMessage = null;
    validateType(types, 'MyTypedef', 3);
    try {
        validateType(types, 'MyTypedef', 5);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 5 (type 'number'), expected type 'MyTypedef' [< 5]");
    try {
        validateType(types, 'MyTypedef', 7);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 7 (type 'number'), expected type 'MyTypedef' [< 5]");
});


test('validateType, typedef attr lte', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'builtin': 'int'},
                'attr': {'lte': 5}
            }
        }
    };
    let errorMessage = null;
    validateType(types, 'MyTypedef', 5);
    try {
        validateType(types, 'MyTypedef', 7);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 7 (type 'number'), expected type 'MyTypedef' [<= 5]");
});


test('validateType, typedef attr gt', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'builtin': 'int'},
                'attr': {'gt': 5}
            }
        }
    };
    let errorMessage = null;
    validateType(types, 'MyTypedef', 7);
    try {
        validateType(types, 'MyTypedef', 3);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 3 (type 'number'), expected type 'MyTypedef' [> 5]");
    try {
        validateType(types, 'MyTypedef', 5);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 5 (type 'number'), expected type 'MyTypedef' [> 5]");
});


test('validateType, typedef attr gte', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'builtin': 'int'},
                'attr': {'gte': 5}
            }
        }
    };
    let errorMessage = null;
    validateType(types, 'MyTypedef', 5);
    try {
        validateType(types, 'MyTypedef', 3);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 3 (type 'number'), expected type 'MyTypedef' [>= 5]");
});


test('validateType, typedef attr lenEq', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'array': {'type': {'builtin': 'int'}}},
                'attr': {'lenEq': 5}
            }
        }
    };
    let errorMessage = null;
    validateType(types, 'MyTypedef', [1, 2, 3, 4, 5]);
    try {
        validateType(types, 'MyTypedef', [1, 2, 3]);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value [1,2,3] (type 'object'), expected type 'MyTypedef' [len == 5]");
});


test('validateType, typedef attr lenEq object', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'dict': {'type': {'builtin': 'int'}}},
                'attr': {'lenEq': 5}
            }
        }
    };
    let errorMessage = null;
    validateType(types, 'MyTypedef', {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5});
    try {
        validateType(types, 'MyTypedef', {'a': 1, 'b': 2, 'c': 3});
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value {\"a\":1,\"b\":2,\"c\":3} (type 'object'), expected type 'MyTypedef' [len == 5]");
});


test('validateType, typedef attr lenLT', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'array': {'type': {'builtin': 'int'}}},
                'attr': {'lenLT': 5}
            }
        }
    };
    let errorMessage = null;
    validateType(types, 'MyTypedef', [1, 2, 3]);
    try {
        validateType(types, 'MyTypedef', [1, 2, 3, 4, 5]);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value [1,2,3,4,5] (type 'object'), expected type 'MyTypedef' [len < 5]");
});


test('validateType, typedef attr lenLTE', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'array': {'type': {'builtin': 'int'}}},
                'attr': {'lenLTE': 5}
            }
        }
    };
    let errorMessage = null;
    validateType(types, 'MyTypedef', [1, 2, 3, 4, 5]);
    try {
        validateType(types, 'MyTypedef', [1, 2, 3, 4, 5, 6, 7]);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value [1,2,3,4,5,6,7] (type 'object'), expected type 'MyTypedef' [len <= 5]");
});


test('validateType, typedef attr lenGT', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'array': {'type': {'builtin': 'int'}}},
                'attr': {'lenGT': 5}
            }
        }
    };
    let errorMessage = null;
    validateType(types, 'MyTypedef', [1, 2, 3, 4, 5, 6, 7]);
    try {
        validateType(types, 'MyTypedef', [1, 2, 3, 4, 5]);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value [1,2,3,4,5] (type 'object'), expected type 'MyTypedef' [len > 5]");
});


test('validateType, typedef attr lenGTE', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'array': {'type': {'builtin': 'int'}}},
                'attr': {'lenGTE': 5}
            }
        }
    };
    let errorMessage = null;
    validateType(types, 'MyTypedef', [1, 2, 3, 4, 5]);
    try {
        validateType(types, 'MyTypedef', [1, 2, 3]);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value [1,2,3] (type 'object'), expected type 'MyTypedef' [len >= 5]");
});


test('validateType, struct', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'string'}},
                    {'name': 'b', 'type': {'builtin': 'int'}},
                    {'name': 'c', 'type': {'builtin': 'float'}},
                    {'name': 'd', 'type': {'builtin': 'bool'}},
                    {'name': 'e', 'type': {'builtin': 'date'}},
                    {'name': 'f', 'type': {'builtin': 'datetime'}},
                    {'name': 'g', 'type': {'builtin': 'uuid'}},
                    {'name': 'h', 'type': {'builtin': 'object'}},
                    {'name': 'i', 'type': {'user': 'MyStruct2'}},
                    {'name': 'j', 'type': {'user': 'MyEnum'}},
                    {'name': 'k', 'type': {'user': 'MyTypedef'}}
                ]
            }
        },
        'MyStruct2': {
            'struct': {
                'name': 'MyStruct2',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'string'}},
                    {'name': 'b', 'type': {'builtin': 'int'}}
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
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'builtin': 'int'},
                'attr': {'gt': 0}
            }
        }
    };

    let obj = {
        'a': 'abc',
        'b': 7,
        'c': 7.1,
        'd': true,
        'e': new Date('2020-06-13'),
        'f': new Date('2020-06-13T13:25:00-07:00'),
        'g': 'a3597528-a253-4c76-bc2d-8da0026cc838',
        'h': {'foo': 'bar'},
        'i': {
            'a': 'abc',
            'b': 7
        },
        'j': 'A',
        'k': 1
    };
    const objValidated = {
        ...obj,
        'e': new Date(2020, 5, 13)
    };
    t.deepEqual(validateType(types, 'MyStruct', obj), objValidated);

    obj = {
        'a': 'abc',
        'b': '7',
        'c': '7.1',
        'd': 'true',
        'e': '2020-06-13',
        'f': '2020-06-13T13:25:00-07:00',
        'g': 'a3597528-a253-4c76-bc2d-8da0026cc838',
        'h': {'foo': 'bar'},
        'i': {
            'a': 'abc',
            'b': '7'
        },
        'j': 'A',
        'k': '1'
    };
    t.deepEqual(validateType(types, 'MyStruct', obj), objValidated);
});


test('validateType, struct map', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}},
                    {'name': 'b', 'type': {'user': 'MyStruct2'}}
                ]
            }
        },
        'MyStruct2': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'c', 'type': {'builtin': 'string'}}
                ]
            }
        }
    };
    const obj = new Map();
    const objB = new Map();
    obj.set('a', 5);
    obj.set('b', objB);
    objB.set('c', 'abc');
    const obj2 = validateType(types, 'MyStruct', obj);
    t.is(obj2 instanceof Map, true);
    t.is(Array.from(obj2.keys()).length, 2);
    t.is(obj2.get('a'), 5);
    t.is(Array.from(obj2.get('b').keys()).length, 1);
    t.is(obj2.get('b') instanceof Map, true);
    t.is(obj2.get('b').get('c'), 'abc');
});


test('validateType, struct empty string', (t) => {
    const types = {
        'Empty': {
            'struct': {
                'name': 'Empty'
            }
        }
    };
    const obj = '';
    t.deepEqual(validateType(types, 'Empty', obj), {});
});


test('validateType, struct string error', (t) => {
    const types = {
        'Empty': {
            'struct': {
                'name': 'Empty'
            }
        }
    };
    let errorMessage = null;
    const obj = 'abc';
    try {
        validateType(types, 'Empty', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'Empty'");
});


test('validateType, struct union', (t) => {
    const types = {
        'MyUnion': {
            'struct': {
                'name': 'MyUnion',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}},
                    {'name': 'b', 'type': {'builtin': 'string'}}
                ],
                'union': true
            }
        }
    };
    let errorMessage = null;

    let obj = {'a': 7};
    t.deepEqual(validateType(types, 'MyUnion', obj), obj);

    obj = {'b': 'abc'};
    t.deepEqual(validateType(types, 'MyUnion', obj), obj);

    obj = {};
    try {
        validateType(types, 'MyUnion', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value {} (type 'object'), expected type 'MyUnion'");

    obj = {'c': 7};
    try {
        validateType(types, 'MyUnion', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Unknown member 'c'");
});


test('validateType, struct base', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'bases': ['MyStruct2'],
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}}
                ]
            }
        },
        'MyStruct2': {
            'struct': {
                'name': 'MyStruct2',
                'bases': ['MyTypedef']
            }
        },
        'MyStruct3': {
            'struct': {
                'name': 'MyStruct3',
                'members': [
                    {'name': 'b', 'type': {'builtin': 'int'}}
                ]
            }
        },
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'user': 'MyStruct3'}
            }
        }
    };
    let errorMessage = null;

    let obj = {'a': 7, 'b': 11};
    t.deepEqual(validateType(types, 'MyStruct', obj), obj);

    obj = {'a': 7};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Required member 'b' missing");
});


test('validateType, struct optional', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}},
                    {'name': 'b', 'type': {'builtin': 'string'}, 'optional': true},
                    {'name': 'c', 'type': {'builtin': 'float'}, 'optional': false}
                ]
            }
        }
    };
    let errorMessage = null;

    let obj = {'a': 7, 'b': 'abc', 'c': 7.1};
    t.deepEqual(validateType(types, 'MyStruct', obj), obj);

    obj = {'a': 7, 'c': 7.1};
    t.deepEqual(validateType(types, 'MyStruct', obj), obj);

    obj = {'a': 7};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Required member 'c' missing");
});


test('validateType, struct nullable', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}},
                    {'name': 'b', 'type': {'builtin': 'int'}, 'attr': {'nullable': true}},
                    {'name': 'c', 'type': {'builtin': 'string'}, 'attr': {'nullable': true}},
                    {'name': 'd', 'type': {'builtin': 'float'}, 'attr': {'nullable': false}}
                ]
            }
        }
    };
    let errorMessage = null;

    let obj = {'a': 7, 'b': 8, 'c': 'abc', 'd': 7.1};
    t.deepEqual(validateType(types, 'MyStruct', obj), obj);

    obj = {'a': 7, 'b': null, 'c': null, 'd': 7.1};
    t.deepEqual(validateType(types, 'MyStruct', obj), obj);

    obj = {'a': 7, 'b': null, 'c': 'null', 'd': 7.1};
    t.deepEqual(validateType(types, 'MyStruct', obj), obj);

    obj = {'a': 7, 'b': 'null', 'c': null, 'd': 7.1};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"null\" (type 'string') for member 'b', expected type 'int'");

    obj = {'a': null, 'b': null, 'c': null, 'd': 7.1};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value null (type 'object') for member 'a', expected type 'int'");

    obj = {'a': 7, 'b': null, 'c': null, 'd': null};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value null (type 'object') for member 'd', expected type 'float'");

    obj = {'a': 7, 'c': null, 'd': 7.1};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Required member 'b' missing");
});


test('validateType, struct nullable attr', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}},
                    {'name': 'b', 'type': {'builtin': 'int'}, 'attr': {'nullable': true, 'lt': 5}}
                ]
            }
        }
    };
    let errorMessage = null;

    let obj = {'a': 7, 'b': 4};
    t.deepEqual(validateType(types, 'MyStruct', obj), obj);

    obj = {'a': 7, 'b': 5};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 5 (type 'number') for member 'b', expected type 'int' [< 5]");

    obj = {'a': 7, 'b': null};
    t.deepEqual(validateType(types, 'MyStruct', obj), obj);
});


test('validateType, struct member attr', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}, 'attr': {'lt': 5}}
                ]
            }
        }
    };
    const obj = {'a': 4};
    t.deepEqual(validateType(types, 'MyStruct', obj), obj);
});


test('validateType, struct member attr invalid', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}, 'attr': {'lt': 5}}
                ]
            }
        }
    };
    let errorMessage = null;
    const obj = {'a': 7};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value 7 (type 'number') for member 'a', expected type 'int' [< 5]");
});


test('validateType, struct error invalid value', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}}
                ]
            }
        }
    };
    let errorMessage = null;
    const obj = 'abc';
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string'), expected type 'MyStruct'");
});


test('validateType, struct error optional null value', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}, 'optional': true}
                ]
            }
        }
    };
    let errorMessage = null;
    const obj = {'a': null};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value null (type 'object') for member 'a', expected type 'int'");
});


test('validateType, struct error member validation', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}}
                ]
            }
        }
    };
    let errorMessage = null;
    const obj = {'a': 'abc'};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string') for member 'a', expected type 'int'");
});


test('validateType, struct error nested member validation', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'user': 'MyStruct2'}}
                ]
            }
        },
        'MyStruct2': {
            'struct': {
                'name': 'MyStruct2',
                'members': [
                    {'name': 'b', 'type': {'builtin': 'int'}}
                ]
            }
        }
    };
    let errorMessage = null;
    const obj = {'a': {'b': 'abc'}};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value \"abc\" (type 'string') for member 'a.b', expected type 'int'");
});


test('validateType, struct error unknown member', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}}
                ]
            }
        }
    };
    let errorMessage = null;
    const obj = {'a': 7, 'b': 8};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Unknown member 'b'");
});


test('validateType, struct error unknown member nested', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}}
                ]
            }
        },
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'array': {'type': {'user': 'MyStruct'}}}
            }
        }
    };
    let errorMessage = null;
    const obj = [{'a': 5}, {'a': 7, 'b': 'abc'}];
    try {
        validateType(types, 'MyTypedef', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Unknown member '1.b'");
});


test('validateType, struct error unknown member empty', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct'
            }
        }
    };
    let errorMessage = null;
    const obj = {'b': 8};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Unknown member 'b'");
});


test('validateType, struct error unknown member long', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}}
                ]
            }
        }
    };
    let errorMessage = null;
    const obj = {'a': 7};
    obj['b'.repeat(2000)] = 8;
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `Unknown member '${'b'.repeat(100)}'`);
});


test('validateType, struct error missing member', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}}
                ]
            }
        }
    };
    let errorMessage = null;
    const obj = {};
    try {
        validateType(types, 'MyStruct', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Required member 'a' missing");
});


test('validateType, action', (t) => {
    const types = {
        'MyAction': {
            'action': {
                'name': 'MyAction'
            }
        }
    };
    let errorMessage = null;
    const obj = {};
    try {
        validateType(types, 'MyAction', obj);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value {} (type 'object'), expected type 'MyAction'");
});


test('validateType, invalid model', (t) => {
    const types = {
        'MyBadBuiltin': {
            'typedef': {
                'name': 'MyBadBuiltin',
                'type': {'builtin': 'foobar'}
            }
        },
        'MyBadType': {
            'typedef': {
                'name': 'MyBadType',
                'type': {'bad_type_key': 'foobar'}
            }
        },
        'MyBadUser': {
            'typedef': {
                'name': 'MyBadUser',
                'type': {'user': 'MyBadUserKey'}
            }
        },
        'MyBadUserKey': {
            'bad_user_key': {}
        }
    };
    t.is(validateType(types, 'MyBadBuiltin', 'abc'), 'abc');
    t.is(validateType(types, 'MyBadType', 'abc'), 'abc');
    t.is(validateType(types, 'MyBadUser', 'abc'), 'abc');
});


//
// validateTypeModelTypes tests
//

test('validateTypeModelTypes', (t) => {
    const validatedTypeModel = validateTypeModelTypes(typeModel.types);
    t.deepEqual(typeModel.types, validatedTypeModel);
    t.not(typeModel.types, validatedTypeModel);
});


test('validateTypeModelTypes, type validation error', (t) => {
    const types = {
        'MyStruct': {
            'struct': {}
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Required member 'MyStruct.struct.name' missing");
});


test('validateTypeModelTypes, struct empty', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct'
            }
        }
    };
    t.deepEqual(types, validateTypeModelTypes(types));
});


test('validateTypeModelTypes, struct inconsistent type name', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct2'
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Inconsistent type name 'MyStruct2' for 'MyStruct'");
});


test('validateTypeModelTypes, struct unknown member type', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'user': 'UnknownType'}}
                ]
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Unknown type 'UnknownType' from 'MyStruct' member 'a'");
});


test('validateTypeModelTypes, struct duplicate member name', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'string'}},
                    {'name': 'b', 'type': {'builtin': 'int'}},
                    {'name': 'a', 'type': {'builtin': 'int'}}
                ]
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Redefinition of 'MyStruct' member 'a'");
});


test('validateTypeModelTypes, struct member attributes', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}, 'attr': {'gt': 0, 'lte': 10}}
                ]
            }
        }
    };
    t.deepEqual(types, validateTypeModelTypes(types));
});


test('validateTypeModelTypes, struct member attributes invalid', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}, 'attr': {'gt': 0, 'lte': 10, 'lenGT': 0, 'lenLTE': 10}}
                ]
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Invalid attribute 'len <= 10' from 'MyStruct' member 'a'
Invalid attribute 'len > 0' from 'MyStruct' member 'a'`);
});


test('validateTypeModelTypes, struct base', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'bases': ['MyStruct2']
            }
        },
        'MyStruct2': {
            'struct': {
                'name': 'MyStruct2',
                'bases': ['MyTypedef']
            }
        },
        'MyStruct3': {
            'struct': {
                'name': 'MyStruct3'
            }
        },
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'user': 'MyStruct3'}
            }
        }
    };
    t.deepEqual(validateTypeModelTypes(types), types);
});


test('validateTypeModelTypes, struct base unknown', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'bases': ['MyStruct2']
            }
        },
        'MyStruct2': {
            'struct': {
                'name': 'MyStruct2',
                'bases': ['Unknown']
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Invalid struct base type 'Unknown'\
`);
});


test('validateTypeModelTypes, struct base typedef unknown', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'bases': ['MyTypedef']
            }
        },
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'user': 'Unknown'}
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Invalid struct base type 'MyTypedef'
Unknown type 'Unknown' from 'MyTypedef'\
`);
});


test('validateTypeModelTypes, struct base non-user', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'bases': ['MyInt']
            }
        },
        'MyInt': {
            'typedef': {
                'name': 'MyInt',
                'type': {'builtin': 'int'}
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Invalid struct base type 'MyInt'\
`);
});


test('validateTypeModelTypes, struct base enum', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'bases': ['MyEnum']
            }
        },
        'MyEnum': {
            'enum': {
                'name': 'MyEnum'
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Invalid struct base type 'MyEnum'\
`);
});


test('validateTypeModelTypes, struct base circular', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'bases': ['MyStruct2']
            }
        },
        'MyStruct2': {
            'struct': {
                'name': 'MyStruct2',
                'bases': ['MyStruct']
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Circular base type detected for type 'MyStruct'
Circular base type detected for type 'MyStruct2'\
`);
});


test('validateTypeModelTypes, struct base union', (t) => {
    const types = {
        'MyStruct': {
            'struct': {
                'name': 'MyStruct',
                'bases': ['MyUnion']
            }
        },
        'MyUnion': {
            'struct': {
                'name': 'MyUnion',
                'union': true
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Invalid struct base type 'MyUnion'\
`);
});


test('validateTypeModelTypes, struct base union struct', (t) => {
    const types = {
        'MyUnion': {
            'struct': {
                'name': 'MyUnion',
                'bases': ['MyStruct'],
                'union': true
            }
        },
        'MyStruct': {
            'struct': {
                'name': 'MyStruct'
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Invalid struct base type 'MyStruct'\
`);
});


test('validateTypeModelTypes, enum empty', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum'
            }
        }
    };
    t.deepEqual(types, validateTypeModelTypes(types));
});


test('validateTypeModelTypes, enum inconsistent type name', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum2'
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Inconsistent type name 'MyEnum2' for 'MyEnum'");
});


test('validateTypeModelTypes,  enum duplicate value', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum',
                'values': [
                    {'name': 'A'},
                    {'name': 'B'},
                    {'name': 'A'}
                ]
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Redefinition of 'MyEnum' value 'A'");
});


test('validateTypeModelTypes, enum base', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum',
                'bases': ['MyEnum2']
            }
        },
        'MyEnum2': {
            'enum': {
                'name': 'MyEnum2',
                'bases': ['MyTypedef']
            }
        },
        'MyEnum3': {
            'enum': {
                'name': 'MyEnum3'
            }
        },
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'user': 'MyEnum3'}
            }
        }
    };
    t.deepEqual(validateTypeModelTypes(types), types);
});


test('validateTypeModelTypes, enum base unknown', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum',
                'bases': ['MyEnum2']
            }
        },
        'MyEnum2': {
            'enum': {
                'name': 'MyEnum2',
                'bases': ['Unknown']
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Invalid enum base type 'Unknown'\
`);
});


test('validateTypeModelTypes, enum base non-user', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum',
                'bases': ['MyInt']
            }
        },
        'MyInt': {
            'typedef': {
                'name': 'MyInt',
                'type': {'builtin': 'int'}
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Invalid enum base type 'MyInt'\
`);
});


test('validateTypeModelTypes, enum base struct', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum',
                'bases': ['MyStruct']
            }
        },
        'MyStruct': {
            'struct': {
                'name': 'MyStruct'
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Invalid enum base type 'MyStruct'\
`);
});


test('validateTypeModelTypes, enum base circular', (t) => {
    const types = {
        'MyEnum': {
            'enum': {
                'name': 'MyEnum',
                'bases': ['MyEnum2']
            }
        },
        'MyEnum2': {
            'enum': {
                'name': 'MyEnum2',
                'bases': ['MyEnum']
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Circular base type detected for type 'MyEnum'
Circular base type detected for type 'MyEnum2'\
`);
});


test('validateTypeModelTypes, array', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'array': {'type': {'builtin': 'int'}}}
            }
        }
    };
    t.deepEqual(types, validateTypeModelTypes(types));
});


test('validateTypeModelTypes, array attributes', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'array': {'type': {'builtin': 'int'}, 'attr': {'gt': 0}}}
            }
        }
    };
    t.deepEqual(types, validateTypeModelTypes(types));
});


test('validateTypeModelTypes, array invalid attribute', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'array': {'type': {'builtin': 'int'}, 'attr': {'lenGT': 0}}}
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid attribute 'len > 0' from 'MyTypedef'");
});


test('validateTypeModelTypes, array unknown type', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'array': {'type': {'user': 'Unknown'}}}
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Unknown type 'Unknown' from 'MyTypedef'");
});


test('validateTypeModelTypes, dict', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'dict': {'type': {'builtin': 'int'}}}
            }
        }
    };
    t.deepEqual(types, validateTypeModelTypes(types));
});


test('validateTypeModelTypes, dict key type', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'dict': {'type': {'builtin': 'int'}, 'keyType': {'user': 'MyEnum'}}}
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
        }
    };
    t.deepEqual(types, validateTypeModelTypes(types));
});


test('validateTypeModelTypes, dict attributes', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'dict': {'type': {'builtin': 'int'}, 'attr': {'gt': 0}}}
            }
        }
    };
    t.deepEqual(types, validateTypeModelTypes(types));
});


test('validateTypeModelTypes, dict key attributes', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'dict': {'type': {'builtin': 'int'}, 'keyType': {'builtin': 'string'}, 'keyAttr': {'lenGT': 0}}}
            }
        }
    };
    t.deepEqual(types, validateTypeModelTypes(types));
});


test('validateTypeModelTypes, dict invalid attribute', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'dict': {'type': {'builtin': 'int'}, 'attr': {'lenGT': 0}}}
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid attribute 'len > 0' from 'MyTypedef'");
});


test('validateTypeModelTypes, dict invalid key attribute', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'dict': {'type': {'builtin': 'int'}, 'keyType': {'builtin': 'string'}, 'keyAttr': {'gt': 0}}}
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid attribute '> 0' from 'MyTypedef'");
});


test('validateTypeModelTypes, dict unknown type', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'dict': {'type': {'user': 'Unknown'}}}
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Unknown type 'Unknown' from 'MyTypedef'");
});


test('validateTypeModelTypes, dict unknown key type', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'dict': {'type': {'builtin': 'int'}, 'keyType': {'user': 'Unknown'}}}
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Unknown type 'Unknown' from 'MyTypedef'
Invalid dictionary key type from 'MyTypedef'`);
});


test('validateTypeModelTypes, typedef invalid attribute', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'user': 'MyStruct'},
                'attr': {'lt': 0}
            }
        },
        'MyStruct': {
            'struct': {
                'name': 'MyStruct'
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid attribute '< 0' from 'MyTypedef'");
});


test('validateTypeModelTypes, typedef nullable', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'user': 'MyStruct'},
                'attr': {'nullable': true}
            }
        },
        'MyStruct': {
            'struct': {
                'name': 'MyStruct'
            }
        }
    };
    t.deepEqual(validateTypeModelTypes(types), types);
});


test('validateTypeModelTypes, typedef attributes', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'user': 'MyTypedef2'},
                'attr': {'gt': 0}
            }
        },
        'MyTypedef2': {
            'typedef': {
                'name': 'MyTypedef2',
                'type': {'builtin': 'int'}
            }
        }
    };
    t.deepEqual(types, validateTypeModelTypes(types));
});


test('validateTypeModelTypes, typedef inconsistent type name', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef2',
                'type': {'builtin': 'int'}
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Inconsistent type name 'MyTypedef2' for 'MyTypedef'");
});


test('validateTypeModelTypes, typedef unknown type', (t) => {
    const types = {
        'MyTypedef': {
            'typedef': {
                'name': 'MyTypedef',
                'type': {'user': 'MyTypedef2'}
            }
        },
        'MyTypedef2': {
            'typedef': {
                'name': 'MyTypedef2',
                'type': {'user': 'MyTypedef3'}
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Unknown type 'MyTypedef3' from 'MyTypedef2'");
});


test('validateTypeModelTypes, action empty struct', (t) => {
    const types = {
        'MyAction': {
            'action': {
                'name': 'MyAction',
                'query': 'MyAction_query'
            }
        },
        'MyAction_query': {
            'struct': {
                'name': 'MyAction_query'
            }
        }
    };
    t.deepEqual(types, validateTypeModelTypes(types));
});


test('validateTypeModelTypes, action inconsistent type name', (t) => {
    const types = {
        'MyAction': {
            'action': {
                'name': 'MyAction2'
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Inconsistent type name 'MyAction2' for 'MyAction'");
});


test('validateTypeModelTypes, action unknown type', (t) => {
    const types = {
        'MyAction': {
            'action': {
                'name': 'MyAction',
                'query': 'Unknown'
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Unknown type 'Unknown' from 'MyAction'");
});


test('validateTypeModelTypes, action action', (t) => {
    const types = {
        'MyAction': {
            'action': {
                'name': 'MyAction',
                'query': 'MyAction2'
            }
        },
        'MyAction2': {
            'action': {
                'name': 'MyAction2'
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid reference to action 'MyAction2' from 'MyAction'");
});


test('validateTypeModelTypes, action duplicate member', (t) => {
    const types = {
        'MyAction': {
            'action': {
                'name': 'MyAction',
                'query': 'MyAction_query',
                'input': 'MyAction_input'
            }
        },
        'MyAction_query': {
            'struct': {
                'name': 'MyAction_query',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}},
                    {'name': 'c', 'type': {'builtin': 'int'}}
                ]
            }
        },
        'MyAction_input': {
            'struct': {
                'name': 'MyAction_input',
                'members': [
                    {'name': 'b', 'type': {'builtin': 'int'}},
                    {'name': 'c', 'type': {'builtin': 'int'}}
                ]
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Redefinition of 'MyAction_input' member 'c'
Redefinition of 'MyAction_query' member 'c'\
`);
});


test('validateTypeModelTypes, action duplicate member inherited', (t) => {
    const types = {
        'MyAction': {
            'action': {
                'name': 'MyAction',
                'query': 'MyAction_query',
                'input': 'MyAction_input'
            }
        },
        'MyAction_query': {
            'struct': {
                'name': 'MyAction_query',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}},
                    {'name': 'c', 'type': {'builtin': 'int'}}
                ]
            }
        },
        'MyAction_input': {
            'struct': {
                'name': 'MyAction_input',
                'bases': ['MyBase'],
                'members': [
                    {'name': 'b', 'type': {'builtin': 'int'}}
                ]
            }
        },
        'MyBase': {
            'struct': {
                'name': 'MyBase',
                'members': [
                    {'name': 'c', 'type': {'builtin': 'int'}}
                ]
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Redefinition of 'MyAction_input' member 'c'
Redefinition of 'MyAction_query' member 'c'\
`);
});


test('validateTypeModelTypes, action duplicate member circular', (t) => {
    const types = {
        'MyAction': {
            'action': {
                'name': 'MyAction',
                'query': 'MyAction_query',
                'input': 'MyAction_input'
            }
        },
        'MyAction_query': {
            'struct': {
                'name': 'MyAction_query',
                'members': [
                    {'name': 'a', 'type': {'builtin': 'int'}},
                    {'name': 'c', 'type': {'builtin': 'int'}}
                ]
            }
        },
        'MyAction_input': {
            'struct': {
                'name': 'MyAction_input',
                'bases': ['MyBase'],
                'members': [
                    {'name': 'b', 'type': {'builtin': 'int'}}
                ]
            }
        },
        'MyBase': {
            'struct': {
                'name': 'MyBase',
                'bases': ['MyAction_input'],
                'members': [
                    {'name': 'c', 'type': {'builtin': 'int'}}
                ]
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModelTypes(types);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Circular base type detected for type 'MyAction_input'
Circular base type detected for type 'MyBase'\
`);
});


//
// validateTypeModel tests
//

test('validateTypeModel', (t) => {
    const testTypeModel = {
        'title': 'My Type Model',
        'types': {
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct'
                }
            }
        }
    };
    const typeModelValidated = validateTypeModel(testTypeModel);
    t.deepEqual(typeModelValidated, testTypeModel);
    t.not(typeModelValidated, testTypeModel);
});


test('validateTypeModel, types error', (t) => {
    const testTypeModel = {
        'title': 'My Type Model',
        'types': {
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct',
                    'members': [
                        {'name': 'a', 'type': {'user': 'Unknown'}}
                    ]
                }
            }
        }
    };
    let errorMessage = null;
    try {
        validateTypeModel(testTypeModel);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `\
Unknown type 'Unknown' from 'MyStruct' member 'a'`);
});
