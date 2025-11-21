# schema-markdown

[![PyPI - Status](https://img.shields.io/pypi/status/schema-markdown)](https://pypi.org/project/schema-markdown/)
[![PyPI](https://img.shields.io/pypi/v/schema-markdown)](https://pypi.org/project/schema-markdown/)
[![GitHub](https://img.shields.io/github/license/craigahobbs/schema-markdown)](https://github.com/craigahobbs/schema-markdown/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/schema-markdown)](https://pypi.org/project/schema-markdown/)

schema-markdown is a schema definition and validation library.


## Links

- [The Schema Markdown Language](https://craigahobbs.github.io/schema-markdown-js/language/)
- [API Documentation](https://craigahobbs.github.io/schema-markdown/)
- [Source code](https://github.com/craigahobbs/schema-markdown)


## Define a Schema

Schemas are defined using the
[Schema Markdown language](https://craigahobbs.github.io/schema-markdown-js/language/),
which is parsed by the
[parse_schema_markdown](https://craigahobbs.github.io/schema-markdown/reference.html#parse-schema-markdown)
function. For example:

~~~ python
from schema_markdown import parse_schema_markdown

model_types = parse_schema_markdown('''\
# An aggregate numerical operation
struct Aggregation

    # The aggregation function - default is "Sum"
    optional AggregationFunction aggregation

    # The numbers to aggregate on
    int[len > 0] numbers

# An aggregation function
enum AggregationFunction
    Average
    Sum
''')
~~~


## Validate using a Schema

To validate an object using the schema, use the
[validate_type](https://craigahobbs.github.io/schema-markdown/reference.html#validate-type)
function. For example:

~~~ python
from schema_markdown import validate_type

validate_type(model_types, 'Aggregation', {'numbers': [1, 2, '3', 4]})

{'numbers': [1, 2, 3, 4]}
~~~

Notice that the numerical input '3' above is *type-massaged* to the integer 3 by validation.

Validation fails if the object does not match the schema:

~~~ python
from schema_markdown import ValidationError

try:
    validate_type(model_types, 'Aggregation', {'numbers': [1, 2, 'asdf', 4]})
except ValidationError as exc:
    str(exc)

"Invalid value 'asdf' (type 'str') for member 'numbers.2', expected type 'int'"
~~~

Validation also fails if a member constraint is violated:

~~~ python
try:
    validate_type(model_types, 'Aggregation', {'numbers': []})
except ValidationError as exc:
    str(exc)

"Invalid value [] (type 'list') for member 'numbers', expected type 'array' [len > 0]"
~~~


## Schema Documentation

You can document a schema with BareScript's
[schemaDoc application](https://craigahobbs.github.io/bare-script-py/library/#var.vGroup='schemaDoc.bare')
running on the
[MarkdownUp application](https://craigahobbs.github.io/markdown-up/).

If your
[type model JSON file](https://craigahobbs.github.io/bare-script-py/model/#var.vURL=''&var.vName='Types')
or
[Schema Markdown file](https://craigahobbs.github.io/schema-markdown-js/language/)
is publicly visible, you can use the BareScript model application with the `var.vURL` query argument:

<https://craigahobbs.github.io/bare-script-py/model/#var.vURL='https://craigahobbs.github.io/bare-script-py/library/model.json'>

**Note:** Schema Markdown files use the `.smd` file extension.


### Self-Hosting Schema Documentation

You can host the schemaDoc application yourself by downloading the
[MarkdownUp Application HTML stub](https://craigahobbs.github.io/markdown-up/#host-markdown-web-pages).

~~~sh
curl -O https://craigahobbs.github.io/markdown-up/extra/index.html
~~~

Replace the MarkdownUp application creation line:

~~~javascript
        const app = new MarkdownUp(window);
~~~

With the following:

```javascript
        const app = new MarkdownUp(window, {
            'markdownText': `\
~~~markdown-script
include <schemaDoc.bare>

schemaDocMain('model.json', 'My Model')
~~~
`
        });
```

To view locally, start a local static web server:

~~~ sh
python3 -m http.server
~~~


## Development

This package is developed using [python-build](https://github.com/craigahobbs/python-build#readme).
It was started using [python-template](https://github.com/craigahobbs/python-template#readme) as follows:

~~~ sh
template-specialize python-template/template/ schema-markdown/ -k package schema-markdown -k name 'Craig A. Hobbs' -k email 'craigahobbs@gmail.com' -k github 'craigahobbs' -k nomain 1
~~~
