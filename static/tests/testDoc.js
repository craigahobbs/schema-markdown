// Licensed under the MIT License
// https://github.com/craigahobbs/schema-markdown/blob/master/LICENSE

/* eslint-disable id-length */
/* eslint-disable max-len */

import {DocPage} from '../src/doc.js';
import browserEnv from 'browser-env';
import test from 'ava';


// Add browser globals
browserEnv(['document', 'window']);


// Mock for window.fetch
class WindowFetchMock {
    static reset(responses) {
        window.fetch = WindowFetchMock.fetch;
        WindowFetchMock.calls = [];
        WindowFetchMock.responses = responses;
    }

    static fetch(resource, init) {
        const response = WindowFetchMock.responses.shift();
        WindowFetchMock.calls.push([resource, init]);
        return {
            'then': (resolve) => {
                if (response.error) {
                    return {
                        'then': () => ({
                            'catch': (reject) => {
                                reject(new Error('Unexpected error'));
                            }
                        })
                    };
                }
                try {
                    resolve({
                        'ok': 'ok' in response ? response.ok : true,
                        'statusText': 'statusText' in response ? response.statusText : 'OK',
                        'json': () => {
                            WindowFetchMock.calls.push('resource response.json');
                        }
                    });
                    return {
                        'then': (resolve2) => {
                            resolve2(response.json);
                            return {
                                // eslint-disable-next-line func-names
                                'catch': function() {
                                    // Do nothing
                                }
                            };
                        }
                    };
                } catch (error) {
                    return {
                        'then': () => ({
                            'catch': (reject) => {
                                reject(error);
                            }
                        })
                    };
                }
            }
        };
    }
}


test('DocPage.run', (t) => {
    window.location.hash = '';
    document.body.innerHTML = '';
    WindowFetchMock.reset([]);

    // Run the application
    const docPage = DocPage.run();
    t.is(document.title, 'The Schema Markdown Type Model');
    t.not(document.body.innerHTML.search('<h2>Structs</h2>'), -1);
    t.not(document.body.innerHTML.search('<a href="blank#name=TypeModel">TypeModel</a>'), -1);

    // Step
    window.location.hash = '#name=TypeModel';
    docPage.windowHashChangeArgs[1]();
    t.is(document.title, 'TypeModel');
    t.not(document.body.innerHTML.search('<a class="linktarget">TypeModel</a>'), -1);
    t.not(document.body.innerHTML.search('<a class="linktarget">typedef Types</a>'), -1);

    // Ensure no calls were made
    t.deepEqual(WindowFetchMock.calls, []);

    // Uninit
    docPage.uninit();

    // Uninit, again, to ensure it does nothing
    docPage.uninit();
});


test('DocPage.run, type model default URL', (t) => {
    window.location.hash = '#';
    document.body.innerHTML = '';
    WindowFetchMock.reset([
        {
            'json': {
                'title': 'All the Types',
                'types': {
                    'MyStruct': {
                        'struct': {
                            'name': 'MyStruct'
                        }
                    }
                }
            }
        }
    ]);

    // Run the application
    const docPage = new DocPage('model.json');
    docPage.render();
    t.is(document.title, 'All the Types');
    t.true(document.body.innerHTML.startsWith('<h1>All the Types</h1>'));
    t.deepEqual(WindowFetchMock.calls, [
        ['model.json', undefined],
        'resource response.json'
    ]);
});


test('DocPage.run, type model URL', (t) => {
    window.location.hash = '#url=model.json';
    document.body.innerHTML = '';
    WindowFetchMock.reset([
        {
            'json': {
                'title': 'All the Types',
                'types': {
                    'MyStruct': {
                        'struct': {
                            'name': 'MyStruct'
                        }
                    }
                }
            }
        }
    ]);

    // Run the application
    const docPage = new DocPage();
    docPage.render();
    t.is(document.title, 'All the Types');
    t.true(document.body.innerHTML.startsWith('<h1>All the Types</h1>'));
    t.deepEqual(WindowFetchMock.calls, [
        ['model.json', undefined],
        'resource response.json'
    ]);
});


test('DocPage.run, type model URL error', (t) => {
    window.location.hash = '#';
    document.body.innerHTML = '';
    WindowFetchMock.reset([
        {
            'ok': false,
            'statusText': 'Not Found',
            'json': {}
        }
    ]);

    // Run the application
    const docPage = new DocPage('types.json');
    docPage.render();
    t.is(document.title, 'Error');
    t.true(document.body.innerHTML.startsWith("<p>Error: Could not fetch type mode 'types.json': Not Found</p>"));
    t.deepEqual(WindowFetchMock.calls, [
        ['types.json', undefined]
    ]);
});


test('DocPage.render, validation error', (t) => {
    const docPage = new DocPage();
    window.location.hash = '#name=';
    WindowFetchMock.reset([]);
    docPage.render();
    t.is(docPage.params, null);
    t.is(document.body.innerHTML, "<p>Error: Invalid value \"\" (type 'string') for member 'name', expected type 'string' [len &gt; 0]</p>");
    t.deepEqual(WindowFetchMock.calls, []);
});


test('DocPage.render, request avoid re-render', (t) => {
    window.location.hash = '#name=TypeModel';
    document.body.innerHTML = '';
    WindowFetchMock.reset([]);

    // Do the render
    const docPage = new DocPage();
    docPage.render();
    t.is(document.title, 'TypeModel');
    t.true(document.body.innerHTML.startsWith('<p>'));
    t.deepEqual(WindowFetchMock.calls, []);

    // Call render again with same name - it should not re-render since its already rendered
    document.body.innerHTML = '';
    docPage.render();
    t.is(document.body.innerHTML, '');
    t.deepEqual(WindowFetchMock.calls, []);

    // Verify render when name is changed
    window.location.hash = '#name=Types';
    docPage.render();
    t.is(document.title, 'Types');
    t.true(document.body.innerHTML.startsWith('<p>'));
    t.deepEqual(WindowFetchMock.calls, []);
});


test('DocPage.render, type model URL index', (t) => {
    window.location.hash = '#';
    document.body.innerHTML = '';
    WindowFetchMock.reset([
        {
            'json': {
                'title': 'All the Types',
                'types': {
                    'MyAction': {
                        'action': {
                            'name': 'MyAction'
                        }
                    },
                    'MyAction2': {
                        'action': {
                            'name': 'MyAction2',
                            'docGroup': 'Stuff'
                        }
                    },
                    'MyStruct': {
                        'struct': {
                            'name': 'MyStruct'
                        }
                    },
                    'MyStruct2': {
                        'struct': {
                            'name': 'MyStruct2',
                            'docGroup': 'Stuff'
                        }
                    },
                    'MyEnum': {
                        'enum': {
                            'name': 'MyEnum'
                        }
                    },
                    'MyEnum2': {
                        'enum': {
                            'name': 'MyEnum2',
                            'docGroup': 'Stuff'
                        }
                    },
                    'MyTypedef': {
                        'typedef': {
                            'name': 'MyTypedef',
                            'type': {'builtin': 'int'}
                        }
                    },
                    'MyTypedef2': {
                        'typedef': {
                            'name': 'MyTypedef2',
                            'docGroup': 'Stuff',
                            'type': {'builtin': 'int'}
                        }
                    }
                }
            }
        }
    ]);

    // Do the render
    const docPage = new DocPage('types.json');
    docPage.render();
    t.is(document.title, 'All the Types');
    t.true(document.body.innerHTML.startsWith('<h1>All the Types</h1>'));
    t.deepEqual(WindowFetchMock.calls, [
        ['types.json', undefined],
        'resource response.json'
    ]);
});


test('DocPage.render, type model unknown type', (t) => {
    window.location.hash = '#name=Unknown';
    document.body.innerHTML = '';
    WindowFetchMock.reset([]);
    const typeModel = {
        'title': 'All the Types',
        'types': {
            'MyStruct': {
                'struct': {
                    'name': 'MyStruct'
                }
            }
        }
    };

    // Do the render
    const docPage = new DocPage(typeModel);
    docPage.render();
    t.is(document.title, 'Error');
    t.is(document.body.innerHTML, "<p>Error: Unknown type name 'Unknown'</p>");
    t.deepEqual(WindowFetchMock.calls, []);
});


test('DocPage.render, type model URL index error', (t) => {
    window.location.hash = '#';
    document.body.innerHTML = '';
    WindowFetchMock.reset([{'error': true}]);

    // Do the render
    const docPage = new DocPage('types.json');
    docPage.render();
    t.is(document.title, 'Error');
    t.is(document.body.innerHTML, '<p>Error: Unexpected error</p>');
    t.deepEqual(WindowFetchMock.calls, [
        ['types.json', undefined]
    ]);
});


test('DocPage.render, command help', (t) => {
    window.location.hash = '#cmd.help=1';
    document.body.innerHTML = '';
    WindowFetchMock.reset([]);

    // Do the render
    const docPage = new DocPage();
    docPage.render();
    t.is(document.title, 'Documentation');
    t.true(document.body.innerHTML.startsWith('<h1 id="cmd.help=1&amp;type_Documentation"><a class="linktarget">Documentation</a></h1>'));
    t.deepEqual(WindowFetchMock.calls, []);
});


test('DocPage.render, command element', (t) => {
    window.location.hash = '#cmd.element=1';
    document.body.innerHTML = '';
    WindowFetchMock.reset([]);

    // Do the render
    const docPage = new DocPage();
    docPage.render();
    t.is(document.title, 'Element');
    t.true(document.body.innerHTML.startsWith('<h1 id="cmd.element=1&amp;type_Element"><a class="linktarget">Element</a></h1>'));
    t.deepEqual(WindowFetchMock.calls, []);
});


test('DocPage.render, command markdown', (t) => {
    window.location.hash = '#cmd.markdown=1';
    document.body.innerHTML = '';
    WindowFetchMock.reset([]);

    // Do the render
    const docPage = new DocPage();
    docPage.render();
    t.is(document.title, 'Markdown');
    t.true(document.body.innerHTML.startsWith('<h1 id="cmd.markdown=1&amp;type_Markdown"><a class="linktarget">Markdown</a></h1>'));
    t.deepEqual(WindowFetchMock.calls, []);
});
