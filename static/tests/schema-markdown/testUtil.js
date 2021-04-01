// Licensed under the MIT License
// https://github.com/craigahobbs/chisel/blob/master/LICENSE

/* eslint-disable id-length */

import {decodeParams, encodeParams, getBaseURL, href, isAbsoluteURL, nbsp} from '../../src/schema-markdown/util.js';
import browserEnv from 'browser-env';
import test from 'ava';


// Add browser globals
browserEnv(['window']);


//
// Constant tests
//

test('nbsp', (t) => {
    t.is(nbsp, String.fromCharCode(160));
});


//
// URL utility tests
//

test('isAbsoluteURL', (t) => {
    t.is(isAbsoluteURL('http://foo.com'), true);
    t.is(isAbsoluteURL('foo/bar.html'), false);
    t.is(isAbsoluteURL(''), false);
});


test('getBaseURL', (t) => {
    t.is(getBaseURL('http://foo.com'), 'http://');
    t.is(getBaseURL('http://foo.com/'), 'http://foo.com/');
    t.is(getBaseURL('http://foo.com/index.html'), 'http://foo.com/');
    t.is(getBaseURL(''), '');
});


//
// href tests
//

test('href', (t) => {
    t.is(
        href(),
        'blank#'
    );
});


test('href, hash', (t) => {
    t.is(
        href({'width': 600, 'height': 400, 'id': null, 'alpha': 'abc'}),
        'blank#alpha=abc&height=400&id=null&width=600'
    );
});


test('href, empty hash', (t) => {
    t.is(
        href({}),
        'blank#'
    );
});


test('href, query', (t) => {
    t.is(
        href(null, {'width': 600, 'height': 400, 'id': null, 'alpha': 'abc'}),
        'blank?alpha=abc&height=400&id=null&width=600'
    );
});


test('href, empty query', (t) => {
    t.is(
        href(null, {}),
        'blank'
    );
});


test('href, pathname', (t) => {
    t.is(
        href(null, null, 'static'),
        'static#'
    );
});


test('href, all', (t) => {
    t.is(
        href(
            {'width': 600, 'height': 400, 'id': null, 'alpha': 'abc'},
            {'width': 600, 'height': 400, 'id': null, 'alpha': 'abc'},
            'static'
        ),
        'static?alpha=abc&height=400&id=null&width=600#alpha=abc&height=400&id=null&width=600'
    );
});


//
// decodeParams tests
//

test('decodeParams, default', (t) => {
    window.location.hash = '_a=7&a=7&b.c=%2Bx%20y%20%2B%20z&b.d.0=2&b.d.1=-4&b.d.2=6';
    t.deepEqual(
        decodeParams(),
        {'a': '7', '_a': '7', 'b': {'c': '+x y + z', 'd': ['2', '-4', '6']}}
    );
});


test('decodeParams, complex dict', (t) => {
    t.deepEqual(
        decodeParams('_a=7&a=7&b.c=%2Bx%20y%20%2B%20z&b.d.0=2&b.d.1=-4&b.d.2=6'),
        {'a': '7', '_a': '7', 'b': {'c': '+x y + z', 'd': ['2', '-4', '6']}}
    );
});


test('decodeParams, array of dicts', (t) => {
    t.deepEqual(
        decodeParams('foo.0.bar=17&foo.0.thud=blue&foo.1.boo=bear'),
        {'foo': [{'bar': '17', 'thud': 'blue'}, {'boo': 'bear'}]}
    );
});


test('decodeParams, top-level array', (t) => {
    t.deepEqual(
        decodeParams('0=1&1=2&2=3'),
        ['1', '2', '3']
    );
});


test('decodeParams, empty query string', (t) => {
    t.deepEqual(
        decodeParams(''),
        {}
    );
});


test('decodeParams, empty string value', (t) => {
    t.deepEqual(
        decodeParams('b='),
        {'b': ''}
    );
});


test('decodeParams, empty string value at end', (t) => {
    t.deepEqual(
        decodeParams('a=7&b='),
        {'a': '7', 'b': ''}
    );
});


test('decodeParams, empty string value at start', (t) => {
    t.deepEqual(
        decodeParams('b=&a=7'),
        {'a': '7', 'b': ''}
    );
});


test('decodeParams, empty string value in middle', (t) => {
    t.deepEqual(
        decodeParams('a=7&b=&c=9'),
        {'a': '7', 'b': '', 'c': '9'}
    );
});


test('decodeParams, decode keys and values', (t) => {
    t.deepEqual(
        decodeParams('a%2eb.c=7%20+%207%20%3d%2014'),
        {'a.b': {'c': '7 + 7 = 14'}}
    );
});


test('decodeParams, decode unicode string', (t) => {
    t.deepEqual(
        decodeParams('a=abc%EA%80%80&b.0=c&b.1=d'),
        {'a': 'abc\ua000', 'b': ['c', 'd']}
    );
});


test('decodeParams, keys and values with special characters', (t) => {
    t.deepEqual(
        decodeParams('a%26b%3Dc%2ed=a%26b%3Dc.d'),
        {'a&b=c.d': 'a&b=c.d'}
    );
});


test('decodeParams, non-initial-zero array-looking index', (t) => {
    t.deepEqual(
        decodeParams('a.1=0'),
        {'a': {'1': '0'}}
    );
});


test('decodeParams, dictionary first, then array-looking zero index', (t) => {
    t.deepEqual(
        decodeParams('a.b=0&a.0=0'),
        {'a': {'b': '0', '0': '0'}}
    );
});


test('decodeParams, empty string key', (t) => {
    t.deepEqual(
        decodeParams('a=7&=b'),
        {'a': '7', '': 'b'}
    );
});


test('decodeParams, empty string key and value', (t) => {
    t.deepEqual(
        decodeParams('a=7&='),
        {'a': '7', '': ''}
    );
});


test('decodeParams, empty string key and value with space', (t) => {
    t.deepEqual(
        decodeParams('a=7& = '),
        {'a': '7', ' ': ' '}
    );
});


test('decodeParams, empty string key with no equal', (t) => {
    t.deepEqual(
        decodeParams('a=7&'),
        {'a': '7'}
    );
});


test('decodeParams, two empty string key/values', (t) => {
    t.deepEqual(
        decodeParams('&'),
        {}
    );
});


test('decodeParams, multiple empty string key/values', (t) => {
    t.deepEqual(
        decodeParams('&&'),
        {}
    );
});


test('decodeParams, empty string sub-key', (t) => {
    t.deepEqual(
        decodeParams('a.=5'),
        {'a': {'': '5'}}
    );
});


test('decodeParams, anchor tag', (t) => {
    t.deepEqual(
        decodeParams('a=7&b'),
        {'a': '7'}
    );
});


test('decodeParams, key with no equal', (t) => {
    let errorMessage = null;
    try {
        decodeParams('a=7&b&c=11');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid key/value pair 'b'");
});


test('decodeParams, key with no equal - long key/value', (t) => {
    let errorMessage = null;
    try {
        decodeParams(`a=7&${'b'.repeat(2000)}&c=11`);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `Invalid key/value pair '${'b'.repeat(100)}'`);
});


test('decodeParams, two empty string keys with no equal', (t) => {
    let errorMessage = null;
    try {
        decodeParams('a&b');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid key/value pair 'a'");
});


test('decodeParams, multiple empty string keys with no equal', (t) => {
    let errorMessage = null;
    try {
        decodeParams('a&b&c');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid key/value pair 'a'");
});


test('decodeParams, duplicate keys', (t) => {
    let errorMessage = null;
    try {
        decodeParams('abc=21&ab=19&abc=17');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Duplicate key 'abc'");
});


test('decodeParams, duplicate keys - long key/value', (t) => {
    let errorMessage = null;
    try {
        decodeParams(`${'a'.repeat(2000)}=21&ab=19&${'a'.repeat(2000)}=17`);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `Duplicate key '${'a'.repeat(100)}'`);
});


test('decodeParams, duplicate index', (t) => {
    let errorMessage = null;
    try {
        decodeParams('a.0=0&a.1=1&a.0=2');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Duplicate key 'a.0'");
});


test('decodeParams, index too large', (t) => {
    let errorMessage = null;
    try {
        decodeParams('a.0=0&a.1=1&a.3=3');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid array index '3' in key 'a.3'");
});


test('decodeParams, index too large - long key/value', (t) => {
    let errorMessage = null;
    try {
        decodeParams(`${'a'.repeat(2000)}.0=0&${'a'.repeat(2000)}.1=1&${'a'.repeat(2000)}.3=3`);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `Invalid array index '3' in key '${'a'.repeat(100)}'`);
});


test('decodeParams, negative index', (t) => {
    let errorMessage = null;
    try {
        decodeParams('a.0=0&a.1=1&a.-3=3');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid array index '-3' in key 'a.-3'");
});


test('decodeParams, invalid index', (t) => {
    let errorMessage = null;
    try {
        decodeParams('a.0=0&a.1asdf=1');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid array index '1asdf' in key 'a.1asdf'");
});


test('decodeParams, first list, then dict', (t) => {
    let errorMessage = null;
    try {
        decodeParams('a.0=0&a.b=0');
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid array index 'b' in key 'a.b'");
});


test('decodeParams, first list, then dict - long key/value', (t) => {
    let errorMessage = null;
    try {
        decodeParams(`${'a'.repeat(2000)}.0=0&${'a'.repeat(2000)}.b=0`);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, `Invalid array index 'b' in key '${'a'.repeat(100)}'`);
});


//
// encodeParams tests
//

test('encodeParams', (t) => {
    t.is(
        encodeParams({
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


test('encodeParams, null', (t) => {
    t.is(encodeParams(null), 'null');
    t.is(encodeParams({'a': null, 'b': 'abc'}), 'a=null&b=abc');
});


test('encodeParams, bool', (t) => {
    t.is(encodeParams(true), 'true');
});


test('encodeParams, number', (t) => {
    t.is(encodeParams(5.1), '5.1');
});


test('encodeParams, date', (t) => {
    t.is(encodeParams(new Date('2020-06-24')), '2020-06-24T00%3A00%3A00.000Z');
});


test('encodeParams, array', (t) => {
    t.is(encodeParams([1, 2, []]), '0=1&1=2&2=');
});


test('encodeParams, empty array', (t) => {
    t.is(encodeParams([]), '');
});


test('encodeParams, empty array/array', (t) => {
    t.is(encodeParams([[]]), '0=');
});


test('encodeParams, object', (t) => {
    t.is(encodeParams({'a': 5, 'b': 'a&b', 'c': {}}), 'a=5&b=a%26b&c=');
});


test('encodeParams, empty object', (t) => {
    t.is(encodeParams({}), '');
});


test('encodeParams, empty object/object', (t) => {
    t.is(encodeParams({'a': {}}), 'a=');
});
