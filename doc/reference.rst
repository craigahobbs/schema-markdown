Reference
=========


decode_query_string
-------------------

.. autofunction:: schema_markdown.decode_query_string


encode_query_string
-------------------

.. autofunction:: schema_markdown.encode_query_string


get_referenced_types
--------------------

    >>> import schema_markdown
    >>> types = {
    ...     'Struct1': {
    ...         'struct': {
    ...             'name': 'Struct1',
    ...             'members': [
    ...                 {'name': 'a', 'type': {'user': 'Struct2'}}
    ...             ]
    ...         }
    ...     },
    ...     'Struct2': {
    ...         'struct': {
    ...             'name': 'Struct2',
    ...             'members': [
    ...                 {'name': 'b', 'type': {'builtin': 'int'}}
    ...             ]
    ...         }
    ...     },
    ...     'MyTypedef': {
    ...         'typedef': {
    ...             'name': 'MyTypedef',
    ...             'type': {'builtin': 'int'},
    ...             'attr': {'lt': 0}
    ...         }
    ...     }
    ... }
    >>> schema_markdown.validate_type_model_types(types) # doctest: +SKIP
    >>> from pprint import pprint
    >>> pprint(schema_markdown.get_referenced_types(types, 'Struct1'))
    {'Struct1': {'struct': {'members': [{'name': 'a', 'type': {'user': 'Struct2'}}],
                            'name': 'Struct1'}},
     'Struct2': {'struct': {'members': [{'name': 'b', 'type': {'builtin': 'int'}}],
                            'name': 'Struct2'}}}

.. autofunction:: schema_markdown.get_referenced_types


JSONEncoder
-----------

.. autoclass:: schema_markdown.JSONEncoder
   :show-inheritance:
   :members:


SchemaMarkdownParser
--------------------

.. autoclass:: schema_markdown.SchemaMarkdownParser
   :members:


SchemaMarkdownParserError
-------------------------

.. autoexception:: schema_markdown.SchemaMarkdownParserError
   :members:


validate_type
-------------

>>> import uuid
>>> parser = schema_markdown.SchemaMarkdownParser('''
... struct MyStruct
...     int a
...     uuid b
... ''')
>>> schema_markdown.validate_type(parser.types, 'MyStruct', {'a': 5, 'b': uuid.UUID('8252121c-7f4f-4b6d-a7e5-f42ca6fdb64c')})
{'a': 5, 'b': UUID('8252121c-7f4f-4b6d-a7e5-f42ca6fdb64c')}

>>> try:
...     schema_markdown.validate_type(parser.types, 'MyStruct', {'a': 5, 'b': 7})
... except schema_markdown.ValidationError as exc:
...     str(exc)
"Invalid value 7 (type 'int') for member 'b', expected type 'uuid'"

.. autofunction:: schema_markdown.validate_type


validate_type_model
-------------------

.. autofunction:: schema_markdown.validate_type_model


validate_type_model_types
-------------------------

    >>> import schema_markdown
    >>> schema_markdown.validate_type_model_types({
    ...     'Struct1': {
    ...         'struct': {
    ...             'name': 'Struct1',
    ...             'members': [
    ...                 {'name': 'a', 'type': {'user': 'Struct2'}}
    ...             ]
    ...         }
    ...     }
    ... }) # doctest: +SKIP
    >>> try:
    ...     schema_markdown.validate_type_model_types({
    ...         'MyStruct': {
    ...             'struct': {}
    ...         }
    ...     })
    ... except Exception as exc:
    ...     f'{exc}'
    "Required member 'MyStruct.struct.name' missing"

.. autofunction:: schema_markdown.validate_type_model_types


ValidationError
---------------

.. autoexception:: schema_markdown.ValidationError
   :members:
