schema-markdown
===============

.. |badge-status| image:: https://img.shields.io/pypi/status/schema-markdown
   :alt: PyPI - Status
   :target: https://pypi.python.org/pypi/schema-markdown/

.. |badge-version| image:: https://img.shields.io/pypi/v/schema-markdown
   :alt: PyPI
   :target: https://pypi.python.org/pypi/schema-markdown/

.. |badge-license| image:: https://img.shields.io/github/license/craigahobbs/schema-markdown
   :alt: GitHub
   :target: https://github.com/craigahobbs/schema-markdown/blob/main/LICENSE

.. |badge-python| image:: https://img.shields.io/pypi/pyversions/schema-markdown
   :alt: PyPI - Python Version
   :target: https://www.python.org/downloads/

|badge-status| |badge-version| |badge-license| |badge-python|


**Schema Markdown** is a human-friendly schema definition language and schema validator. Here are
its features at a glance:

- Schema-validate JSON objects
- Human-friendly schema definition
- Validates member value and length contraints
- Validation *type-massages* string member values
- Pure Python


Links
-----

- `Schema Markdown Language Reference <https://craigahobbs.github.io/schema-markdown/schema-markdown.html>`__
- `Documentation on GitHub Pages <https://craigahobbs.github.io/schema-markdown/>`__
- `Package on pypi <https://pypi.org/project/schema-markdown/>`__
- `Source code on GitHub <https://github.com/craigahobbs/schema-markdown>`__


Usage
-----

To schema-validate an object, first parse its *Schema Markdown* using the
`SchemaMarkdownParser <https://craigahobbs.github.io/schema-markdown/reference.html#schemamarkdownparser>`__
class:

>>> import schema_markdown
...
>>> parser = schema_markdown.SchemaMarkdownParser('''\
... # An aggregation function
... enum Aggregation
...     Average
...     Sum
...
... # An aggregate numerical operation
... struct Operation
...     # The aggregation function - default is "Sum"
...     optional Aggregation aggregation
...
...     # The numbers to operate on
...     int[len > 0] numbers
... ''')

Then, validate a dictionary object (or other object) using the
`validate_type <https://craigahobbs.github.io/schema-markdown/reference.html#validate-type>`__
function:

>>> schema_markdown.validate_type(parser.types, 'Operation', {
...     'numbers': [1, 2, '3', 4]
... })
{'numbers': [1, 2, 3, 4]}

Notice that the numerical input '3' above is *type-massaged* to the integer 3 by validation.
Validation fails if the object does not match the schema:

>>> try:
...     schema_markdown.validate_type(parser.types, 'Operation', {
...         'numbers': [1, 2, 'asdf', 4]
...     })
... except schema_markdown.ValidationError as exc:
...     str(exc)
"Invalid value 'asdf' (type 'str') for member 'numbers.2', expected type 'int'"

Validation also fails if a member contraint is violated:

>>> try:
...     schema_markdown.validate_type(parser.types, 'Operation', {
...         'numbers': []
...     })
... except schema_markdown.ValidationError as exc:
...     str(exc)
"Invalid value [] (type 'list') for member 'numbers', expected type 'array' [len > 0]"


Development
-----------

This project is developed using `python-build <https://github.com/craigahobbs/python-build#readme>`__. It was started
using `python-template <https://github.com/craigahobbs/python-template#readme>`__ as follows::

    template-specialize python-template/template/ schema-markdown/ -k package schema-markdown -k name 'Craig A. Hobbs' -k email 'craigahobbs@gmail.com' -k github 'craigahobbs'
