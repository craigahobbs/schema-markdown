// Licensed under the MIT License
// https://github.com/craigahobbs/schema-markdown/blob/master/LICENSE

/* eslint-disable id-length */

import {decodeQueryString, encodeHref, encodeQueryString} from '../../src/schema-markdown/encode.js';
import browserEnv from 'browser-env';
import test from 'ava';


// Add browser globals
browserEnv(['window']);


//
// href tests
//

test('href', (t) => {
    t.is(
        encodeHref(),
        'blank#'
    );
});


test('href, hash', (t) => {
    t.is(
        encodeHref({'width': 600, 'height': 400, 'id': null, 'alpha': 'abc'}),
        'blank#alpha=abc&height=400&id=null&width=600'
    );
});


test('href, empty hash', (t) => {
    t.is(
        encodeHref({}),
        'blank#'
    );
});


test('href, query', (t) => {
    t.is(
        encodeHref(null, {'width': 600, 'height': 400, 'id': null, 'alpha': 'abc'}),
        'blank?alpha=abc&height=400&id=null&width=600'
    );
});


test('href, empty query', (t) => {
    t.is(
        encodeHref(null, {}),
        'blank'
    );
});


test('href, pathname', (t) => {
    t.is(
        encodeHref(null, null, 'static'),
        'static#'
    );
});


test('href, all', (t) => {
    t.is(
        encodeHref(
            {'width': 600, 'height': 400, 'id': null, 'alpha': 'abc'},
            {'width': 600, 'height': 400, 'id': null, 'alpha': 'abc'},
            'static'
        ),
        'static?alpha=abc&height=400&id=null&width=600#alpha=abc&height=400&id=null&width=600'
    );
});


//
// decodeQueryString tests
//

test('decodeQueryString, default', (t) => {
    window.location.hash = '_a=7&a=7&b.c=%2Bx%20y%20%2B%20z&b.d.0=2&b.d.1=-4&b.d.2=6';
    t.deepEqual(
        decodeQueryString(),
        {'a': '7', '_a': '7', 'b': {'c': '+x y + z', 'd': ['2', '-4', '6']}}
    );
});


test('decodeQueryString, complex dict', (t) => {
    t.deepEqual(
        decodeQueryString('_a=7&a=7&b.c=%2Bx%20y%20%2B%20z&b.d.0=2&b.d.1=-4&b.d.2=6'),
        {'a': '7', '_a': '7', 'b': {'c': '+x y + z', 'd': ['2', '-4', '6']}}
    );
});


test('decodeQueryString, array of dicts', (t) => {
    t.deepEqual(
        decodeQueryString('foo.0.bar=17&foo.0.thud=blue&foo.1.boo=bear'),
        {'foo': [{'bar': '17', 'thud': 'blue'}, {'boo': 'bear'}]}
    );
});


test('decodeQueryString, top-level array', (t) => {
    t.deepEqual(
        decodeQueryString('0=1&1=2&2=3'),
        ['1', '2', '3']
    );
});


test('decodeQueryString, empty query string', (t) => {
    t.deepEqual(
        decodeQueryString(''),
        {}
    );
});


test('decodeQueryString, empty string value', (t) => {
    t.deepEqual(
        decodeQueryString('b='),
        {'b': ''}
    );
});


test('decodeQueryString, empty string value at end', (t) => {
    t.deepEqual(
        decodeQueryString('a=7&b='),
        {'a': '7', 'b': ''}
    );
});


test('decodeQueryString, empty string value at start', (t) => {
    t.deepEqual(
        decodeQueryString('b=&a=7'),
        {'a': '7', 'b': ''}
    );
});


test('decodeQueryString, empty string value in middle', (t) => {
    t.deepEqual(
        decodeQueryString('a=7&b=&c=9'),
        {'a': '7', 'b': '', 'c': '9'}
    );
});


test('decodeQueryString, decode keys and values', (t) => {
    t.deepEqual(
        decodeQueryString('a%2eb.c=7%20+%207%20%3d%2014'),
        {'a.b': {'c': '7 + 7 = 14'}}
    );
});


test('decodeQueryString, decode unicode string', (t) => {
    t.deepEqual(
        decodeQueryString('a=abc%EA%80%80&b.0=c&b.1=d'),
        {'a': 'abc\ua000', 'b': ['c', 'd']}
    );
});


test('decodeQueryString, keys and values with special characters', (t) => {
    t.deepEqual(
        decodeQueryString('a%26b%3Dc%2ed=a%26b%3Dc.d'),
        {'a&b=c.d': 'a&b=c.d'}
    );
});


test('decodeQueryString, non-initial-zero array-looking index', (t) => {
    t.deepEqual(
        decodeQueryString('a.1=0'),
        {'a': {'1': '0'}}
    );
});


test('decodeQueryString, dictionary first, then array-looking zero index', (t) => {
    t.deepEqual(
        decodeQueryString('a.b=0&a.0=0'),
        {'a': {'b': '0', '0': '0'}}
    );
});


test('decodeQueryString, empty string key', (t) => {
    t.deepEqual(
        decodeQueryString('a=7&=b'),
        {'a': '7', '': 'b'}
    );
});


test('decodeQueryString, empty string key and value', (t) => {
    t.deepEqual(
        decodeQueryString('a=7&='),
        {'a': '7', '': ''}
    );
});


test('decodeQueryString, empty string key and value with space', (t) => {
    t.deepEqual(
        decodeQueryString('a=7& = '),
        {'a': '7', ' ': ' '}
    );
});


test('decodeQueryString, empty string key with no equal', (t) => {
    t.deepEqual(
        decodeQueryString('a=7&'),
        {'a': '7'}
    );
});


test('decodeQueryString, two empty string key/values', (t) => {
    t.deepEqual(
        decodeQueryString('&'),
        {}
    );
});


test('decodeQueryString, multiple empty string key/values', (t) => {
    t.deepEqual(
        decodeQueryString('&&'),
        {}
    );
});


test('decodeQueryString, empty string sub-key', (t) => {
    t.deepEqual(
        decodeQueryString('a.=5'),
        {'a': {'': '5'}}
    );
});


test('decodeQueryString, anchor tag', (t) => {
    t.deepEqual(
        decodeQueryString('a=7&b'),
        {'a': '7'}
    );
});


test('decodeQueryString, key with no equal', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString('a=7&b&c=11');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid key/value pair 'b'");
});


test('decodeQueryString, key with no equal - long key/value', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString(`a=7&${'b'.repeat(2000)}&c=11`);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `Invalid key/value pair '${'b'.repeat(100)}'`);
});


test('decodeQueryString, two empty string keys with no equal', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString('a&b');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid key/value pair 'a'");
});


test('decodeQueryString, multiple empty string keys with no equal', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString('a&b&c');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid key/value pair 'a'");
});


test('decodeQueryString, duplicate keys', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString('abc=21&ab=19&abc=17');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Duplicate key 'abc'");
});


test('decodeQueryString, duplicate keys - long key/value', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString(`${'a'.repeat(2000)}=21&ab=19&${'a'.repeat(2000)}=17`);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `Duplicate key '${'a'.repeat(100)}'`);
});


test('decodeQueryString, duplicate index', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString('a.0=0&a.1=1&a.0=2');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Duplicate key 'a.0'");
});


test('decodeQueryString, index too large', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString('a.0=0&a.1=1&a.3=3');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid array index '3' in key 'a.3'");
});


test('decodeQueryString, index too large - long key/value', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString(`${'a'.repeat(2000)}.0=0&${'a'.repeat(2000)}.1=1&${'a'.repeat(2000)}.3=3`);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `Invalid array index '3' in key '${'a'.repeat(100)}'`);
});


test('decodeQueryString, negative index', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString('a.0=0&a.1=1&a.-3=3');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid array index '-3' in key 'a.-3'");
});


test('decodeQueryString, invalid index', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString('a.0=0&a.1asdf=1');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid array index '1asdf' in key 'a.1asdf'");
});


test('decodeQueryString, first list, then dict', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString('a.0=0&a.b=0');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid array index 'b' in key 'a.b'");
});


test('decodeQueryString, first list, then dict - long key/value', (t) => {
    let errorMessage = null;
    try {
        decodeQueryString(`${'a'.repeat(2000)}.0=0&${'a'.repeat(2000)}.b=0`);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `Invalid array index 'b' in key '${'a'.repeat(100)}'`);
});


//
// encodeQueryString tests
//

test('encodeQueryString', (t) => {
    t.is(
        encodeQueryString({
            'foo': 17,
            'bar': 19.33,
            'bonk': 'abc',
            ' th&ud ': ' ou&ch ',
            'blue': new Date('2020-06-24'),
            'fever': null,
            'zap': [
                {'a': 5},
                {'b': 7}
            ]
        }),
        '%20th%26ud%20=%20ou%26ch%20&bar=19.33&blue=2020-06-24T00%3A00%3A00.000Z&bonk=abc&fever=null&foo=17&zap.0.a=5&zap.1.b=7'
    );
});


test('encodeQueryString, null', (t) => {
    t.is(encodeQueryString(null), 'null');
    t.is(encodeQueryString({'a': null, 'b': 'abc'}), 'a=null&b=abc');
});


test('encodeQueryString, bool', (t) => {
    t.is(encodeQueryString(true), 'true');
});


test('encodeQueryString, number', (t) => {
    t.is(encodeQueryString(5.1), '5.1');
});


test('encodeQueryString, date', (t) => {
    t.is(encodeQueryString(new Date('2020-06-24')), '2020-06-24T00%3A00%3A00.000Z');
});


test('encodeQueryString, array', (t) => {
    t.is(encodeQueryString([1, 2, []]), '0=1&1=2&2=');
});


test('encodeQueryString, empty array', (t) => {
    t.is(encodeQueryString([]), '');
});


test('encodeQueryString, empty array/array', (t) => {
    t.is(encodeQueryString([[]]), '0=');
});


test('encodeQueryString, object', (t) => {
    t.is(encodeQueryString({'a': 5, 'b': 'a&b', 'c': {}}), 'a=5&b=a%26b&c=');
});


test('encodeQueryString, empty object', (t) => {
    t.is(encodeQueryString({}), '');
});


test('encodeQueryString, empty object/object', (t) => {
    t.is(encodeQueryString({'a': {}}), 'a=');
});
