Command-Line Tool
=================

The ``schema_markdown`` package can be used as a command like tool like so:

.. code-block:: sh

   $ python3 -m schema_markdown --help
   usage: schema_markdown [-h] {compile,validate,model} ...

   positional arguments:
     {compile,validate,model}
       compile             Parse Schema Markdown files
       validate            Schema-validate JSON files
       model               Dump the type model

   options:
     -h, --help            show this help message and exit

The **compile** command compiles one or more :ref:`parser` files and outputs a :ref:`schema`
``TypeModel`` object:

.. code-block:: text

   usage: schema_markdown compile [-h] [-o PATH] [--compact] [paths ...]

   positional arguments:
     paths       Schema Markdown file paths. If none, default is stdin.

   options:
     -h, --help  show this help message and exit
     -o PATH     Optional JSON type model output file path. Default is stdout.
     --compact   Generate compact JSON

The **validate** command parses a :ref:`parser` file and a type and schema-validates one or more
JSON files:

.. code-block:: text

   usage: schema_markdown validate [-h] schema type [paths ...]

   positional arguments:
     schema      Schema Markdown file path
     type        Name of type to validate
     paths       JSON file paths to validate. If none, defaults is stdin.

   options:
     -h, --help  show this help message and exit

The **model** command dumps the :ref:`schema`'s type model:

.. code-block:: text

   usage: schema_markdown model [-h] [-o PATH] [--compact]

   options:
     -h, --help  show this help message and exit
     -o PATH     Optional JSON type model output file path. Default is stdout.
     --compact   Generate compact JSON
