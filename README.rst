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


schema-markdown is a schema definition and validation library.


Links
-----

- `The Schema Markdown Language <https://craigahobbs.github.io/schema-markdown-js/language/>`__
- `API Documentation <https://craigahobbs.github.io/schema-markdown/>`__
- `Source code <https://github.com/craigahobbs/schema-markdown>`__


Define a Schema
---------------

Schemas are defined using the
`Schema Markdown language <https://craigahobbs.github.io/schema-markdown-js/language/>`__,
which is parsed by the
`parse_schema_markdown <https://craigahobbs.github.io/schema-markdown/reference.html#parse-schema-markdown>`__
function. For example:

>>> from schema_markdown import parse_schema_markdown
...
>>> model_types = parse_schema_markdown('''\
... # An aggregate numerical operation
... struct Aggregation
...
...     # The aggregation function - default is "Sum"
...     optional AggregationFunction aggregation
...
...     # The numbers to aggregate on
...     int[len > 0] numbers
...
... # An aggregation function
... enum AggregationFunction
...     Average
...     Sum
... ''')


Validate using a Schema
-----------------------

To validate an object using the schema, use the
`validate_type <https://craigahobbs.github.io/schema-markdown/reference.html#validate-type>`__
function. For example:

>>> from schema_markdown import validate_type
...
>>> validate_type(model_types, 'Aggregation', {'numbers': [1, 2, '3', 4]})
{'numbers': [1, 2, 3, 4]}

Notice that the numerical input '3' above is *type-massaged* to the integer 3 by validation.

Validation fails if the object does not match the schema:

>>> from schema_markdown import ValidationError
...
>>> try:
...     validate_type(model_types, 'Aggregation', {'numbers': [1, 2, 'asdf', 4]})
... except ValidationError as exc:
...     str(exc)
"Invalid value 'asdf' (type 'str') for member 'numbers.2', expected type 'int'"

Validation also fails if a member constraint is violated:

>>> try:
...     validate_type(model_types, 'Aggregation', {'numbers': []})
... except ValidationError as exc:
...     str(exc)
"Invalid value [] (type 'list') for member 'numbers', expected type 'array' [len > 0]"


Document a Schema
-----------------

To document the schema, download the
`documentation application <https://github.com/craigahobbs/schema-markdown-doc#the-schema-markdown-documentation-viewer>`__
stub and save the type model as JSON:

.. code-block:: sh

   curl -O https://craigahobbs.github.io/schema-markdown-doc/extra/index.html
   python3 \
       -c 'from model import model_types; import json; print(json.dumps(model_types))' \
       > model.json

To host locally, start a local static web server:

.. code-block:: sh

   python3 -m http.server


Development
-----------

This package is developed using `python-build <https://github.com/craigahobbs/python-build#readme>`__.
It was started using `python-template <https://github.com/craigahobbs/python-template#readme>`__ as follows:

.. code-block:: sh

   template-specialize python-template/template/ schema-markdown/ -k package schema-markdown -k name 'Craig A. Hobbs' -k email 'craigahobbs@gmail.com' -k github 'craigahobbs' -k nomain 1
