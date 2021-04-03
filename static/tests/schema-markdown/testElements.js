// Licensed under the MIT License
// https://github.com/craigahobbs/schema-markdown/blob/master/LICENSE

/* eslint-disable id-length */

import {getBaseURL, isAbsoluteURL, nbsp, renderElements, validateElements} from '../../src/schema-markdown/elements.js';
import browserEnv from 'browser-env';
import test from 'ava';


// Add browser globals
browserEnv(['document']);


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
// validateElements tests
//

test('validateElements', (t) => {
    const elements = {
        'html': 'html',
        'elem': [
            {
                'html': 'h1',
                'elem': {'text': 'Title'}
            },
            {
                'html': 'p',
                'attr': null,
                'elem': [
                    {'text': 'This is some '},
                    {'html': 'span', 'attr': {'style': 'font-weight: bold;'}, 'elem': {'text': 'bolded text!'}}
                ]
            }
        ]
    };
    validateElements(elements);
    t.pass();
});


test('validateElements, error element type', (t) => {
    const elements = {
        'html': 'html',
        'elem': [0]
    };
    let errorMessage = null;
    try {
        validateElements(elements);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid element 0 (type 'number')");
});


test('validateElements, error element model validation', (t) => {
    const elements = {
        'html': 'html',
        'unknown': 'abc'
    };
    let errorMessage = null;
    try {
        validateElements(elements);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Unknown member 'unknown'");
});


test('validateElements, error missing element key', (t) => {
    const elements = {};
    let errorMessage = null;
    try {
        validateElements(elements);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Missing element key {} (type 'object')");
});


test('validateElements, null callback value', (t) => {
    const elements = {'html': 'span', 'attr': {'style': null}, 'callback': null};
    let errorMessage = null;
    try {
        validateElements(elements);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid value null (type 'object') for member 'callback', expected type 'object'");
});


test('validateElements, invalid callback value', (t) => {
    const elements = {'html': 'span', 'attr': {'style': null}, 'callback': 0};
    let errorMessage = null;
    try {
        validateElements(elements);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, "Invalid element callback function 0 (type 'number')");
});


test('validateElements, error text element with attr', (t) => {
    const elements = {'text': 'abc', 'attr': null};
    let errorMessage = null;
    try {
        validateElements(elements);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, 'Invalid text element member "attr" "abc" (type \'string\')');
});


test('validateElements, error text element with elem', (t) => {
    const elements = {'text': 'abc', 'elem': null};
    let errorMessage = null;
    try {
        validateElements(elements);
    } catch ({message}) {
        errorMessage = message;
    }
    t.is(errorMessage, 'Invalid text element member "elem" "abc" (type \'string\')');
});


//
// renderElements tests
//

test('renderElements', (t) => {
    document.body.innerHTML = '';
    renderElements(document.body, {'html': 'div'});
    t.is(document.body.innerHTML, '<div></div>');
    renderElements(document.body, [{'html': 'div'}, {'html': 'div', 'attr': {'id': 'Id'}}]);
    t.is(document.body.innerHTML, '<div></div><div id="Id"></div>');
    renderElements(document.body, {'html': 'div'}, false);
    t.is(document.body.innerHTML, '<div></div><div id="Id"></div><div></div>');
    renderElements(document.body, null);
    t.is(document.body.innerHTML, '');
    renderElements(document.body);
    t.is(document.body.innerHTML, '');
});


test('renderElements, basic', (t) => {
    renderElements(document.body, [
        {'html': 'h1', 'elem': {'text': 'Hello, World!'}},
        [
            {'html': 'p', 'elem': [{'text': 'Word'}]},
            {'html': 'p', 'elem': [{'text': 'Two'}, {'text': 'Words'}]},
            {'html': 'p', 'elem': []},
            {'html': 'p', 'elem': null}
        ],
        {'html': 'div', 'attr': {'id': 'Id', 'class': null}}
    ]);
    t.is(
        document.body.innerHTML,
        '<h1>Hello, World!</h1><p>Word</p><p>TwoWords</p><p></p><p></p><div id="Id"></div>'
    );
});


test('renderElements, non-string attribute value', (t) => {
    const elements = {'html': 'span', 'attr': {'style': 0}};
    validateElements(elements);
    renderElements(document.body, elements);
    t.is(
        document.body.innerHTML,
        '<span style="0"></span>'
    );
});


test('renderElements, svg', (t) => {
    renderElements(document.body, [
        {'svg': 'svg', 'attr': {'width': '600', 'height': '400'}, 'elem': [
            {
                'svg': 'rect',
                'attr': {'x': '10', 'y': '10', 'width': '20', 'height': '20', 'style': 'fill: #ff0000;'}
            },
            {
                'svg': 'rect',
                'attr': {'x': '10', 'y': '10', 'width': '20', 'height': '20', 'style': 'fill: #00ff00;'}
            }
        ]}
    ]);
    t.is(
        document.body.innerHTML,
        '<svg width="600" height="400">' +
            '<rect x="10" y="10" width="20" height="20" style="fill: #ff0000;"></rect>' +
            '<rect x="10" y="10" width="20" height="20" style="fill: #00ff00;"></rect>' +
            '</svg>'
    );
});


test('renderElements, element callback', (t) => {
    let callbackCount = 0;
    const callback = (element) => {
        t.true(typeof element !== 'undefined');
        callbackCount += 1;
    };
    renderElements(document.body, [
        {'html': 'div', 'callback': callback}
    ]);
    t.is(
        document.body.innerHTML,
        '<div></div>'
    );
    t.is(callbackCount, 1);
});
