Schema Markdown
===============

Schema Markdown is a human-friendly schema definition language. It is used to define structure
types, enumeration types, typedef types, and actions (JSON APIs). Schema Markdown parsing is done by
the :ref:`reference:SchemaMarkdownParser` class. For example:

>>> parser = schema_markdown.SchemaMarkdownParser('''
... # A number pair structure
... struct NumberPair
...     # The first number of the pair
...     float first
...
...     # The second number of the pair
...     float second
...
... # A number pair list type
... typedef NumberPair[len > 0] NumberPairList
...
... # Color enumeration
... enum Colors
...     # A rose by any other color...
...     Red
...     Blue
...     Green
... ''')

The parser's `types` member contains the schema's :ref:`type-model:Type Model` dictionary:

>>> sorted(parser.types.keys())
['Colors', 'NumberPair', 'NumberPairList']

The type model is used to validate objects in concunction with the
:ref:`reference:validate_type` function.


Comments
--------

Schema Markdown comments are lines beginning with the "#" character preceded only by whitespace.
Comments are interpreted as documentation markdown text lines to be applied to the next Schema
Markdown definition. If you want a non-documentation comment use the "#-" form of commment.


Built-in Types
--------------

Schema Markdown contains the following built-in types:

- ``bool`` - a boolean

- ``date`` - a :class:`~datetime.date`

- ``datetime`` - a :class:`~datetime.datetime`

- ``float`` - a floating point number

- ``int`` - an integer number

- ``object`` - a generic, unvalidated object (use sparingly)

- ``string`` - a string

- ``uuid`` - a :class:`~uuid.UUID`


Structure Types
----------------

Structure definitions contain zero or more member definitions. Member definitions may take the
following forms:

>>> parser = schema_markdown.SchemaMarkdownParser('''
... # My test struct
... struct MyStruct
...     # A required member
...     int a
...
...     # A member with type attributes
...     int(> 0) b
...
...     # An optional member
...     optional float c
...
...     # An optional, nullable member - value may be null
...     optional string(nullable) d
...
...     # An array member
...     bool[] e
...
...     # An array member with type attributes
...     string(len > 0)[len > 0] f
...
...     # A dictionary member
...     date{} g
...
...     # A dictionary member with attributes
...     date{len > 0} h
...
...     # A dictionary member with key type
...     MyEnum : uuid{} i
...
... enum MyEnum
...     A
...     B
... ''')
...
>>> try:
...     schema_markdown.validate_type(parser.types, 'MyStruct', {})
... except schema_markdown.ValidationError as exc:
...     str(exc)
"Required member 'a' missing"


Typedefs
--------

Typedefs are a type definition and its associated attributes. For example:

>>> parser = schema_markdown.SchemaMarkdownParser('''
... typedef int(> 0) PositiveInt
... ''')
...
>>> try:
...     schema_markdown.validate_type(parser.types, 'PositiveInt', -9)
... except schema_markdown.ValidationError as exc:
...     str(exc)
"Invalid value -9 (type 'int'), expected type 'PositiveInt' [> 0.0]"


Type Attributes
---------------

Type attributes are used to add validation constraints to struct members and typedefs.

The following type attributes are available for ``int`` and ``float`` types:

- "< ``number``" - the value is less than a number

- "<= ``number``" - the value is less than or equal to a number

- "> ``number``" - the value is greater than a number

- ">= ``number``" - the value is less greater or equal to a number

- "== ``number``" - the value is equal to a number

The following type attributes are available for ``string``, array, and dictionary types:

- "len < ``integer``" - the length is less than an integer

- "len <= ``integer``" - the length is less than or equal to an integer

- "len > ``integer``" - the length is greater than an integer

- "len >= ``integer``" - the length is greater than or equal to an integer

- "len == ``integer``" - the length is equal to an integer


Enumeration Types
-----------------

An enumeration is a set of enumeration value strings. An enumeration member will validate only
strings in the enumeration value set. For example:

>>> parser = schema_markdown.SchemaMarkdownParser('''
... # My test enumeration
... enum TestEnum
...     # An enumeration value
...     Value1
...
...     # Another enumeration value
...     Value2
...
...     # A quoted enumeration value
...     "Value 3"
... ''')
...
>>> try:
...     schema_markdown.validate_type(parser.types, 'TestEnum', 'Value4')
... except schema_markdown.ValidationError as exc:
...     str(exc)
"Invalid value 'Value4' (type 'str'), expected type 'TestEnum'"


Actions
-------

Actions are JSON APIs defined using the "action" keyword as shown above. For example:

>>> parser = schema_markdown.SchemaMarkdownParser('''
... # Sum a list of number pairs
... action sum_number_pairs
...     urls
...         GET
...     query
...         # The list of number pairs to sum
...         int[len > 0] numbers
...     output
...         # The sum of the numbers
...         int sum
...     errors
...         # The number list contains a negative number
...         NegativeNumber
... ''')

Actions can contain any the following sections:

- "urls" - Contains a list of URL status/path specifications. By default actions are hosted as
  "POST" at the default URL path ("/my_action" if the action is named "my_action). URL
  specifications can have the follow forms:

  - ``GET`` - Match the HTTP request method with the default path
  - ``GET /path/`` - Match the HTTP request method and the exact path
  - ``* /path/`` - Match any HTTP request method and the exact path
  - ``GET /path/{name}`` - A URL path with a **path parameter** called "name". Path parameters
    should have a corresponding member in the "path" section.

- "path" - The path parameters structure type - see `Structure Types`_ below

- "query" - The query string parameters structure type - see `Structure Types`_ below

- "input" - The request JSON content parameters structure type - see `Structure Types`_ below

- "output" - The response JSON content parameters structure type - see `Structure Types`_ below

- "errors" - The action's custom error code enumeration type - see `Enumeration Types`_ below


Inheritance
-----------

Structure types can multiple-inherit members from other structure types. For example:

>>> parser = schema_markdown.SchemaMarkdownParser('''
... struct s1
...     int a
...
... struct s2
...     string b
...
... struct s3 (s1, s2)
...     datetime c
... ''')

Structure inheritance also works for the ``path``, ``query``, ``input``, and ``output`` action
structure sections.

>>> parser = schema_markdown.SchemaMarkdownParser('''
... struct s1
...     int a
...
... struct s2
...     string b
...
... action my_action
...     query (s1, s2)
...         datetime c
... ''')

Likewise, enumeration types can inerit values from other enumeration types:

>>> parser = schema_markdown.SchemaMarkdownParser('''
... enum e1
...     A
...
... enum e2
...     B
...
... enum e3 (e1, e2)
...     C
... ''')


Documentation Groups
--------------------

Schema Markdown user types can be grouped for documentation purposes. To set an active documentation
group, use the ``group`` keyword with a group name string. The group applies to all types defined
afterward. To clear the active documentation group, use the ``group`` keyword without a string.

>>> parser = schema_markdown.SchemaMarkdownParser('''
... # This struct has no documentation group
... struct Struct1
...
... group "Stuff"
...
... # This struct is a member of documentation group "Stuff"
... struct Struct2
...
... # This struct is also a member of documentation group "Stuff"
... struct Struct3
...
... group "Other Stuff"
...
... # This struct is also a member of documentation group "Other Stuff"
... struct Struct4
...
... group
...
... # This struct has no documentation group
... struct Struct5
... ''')
