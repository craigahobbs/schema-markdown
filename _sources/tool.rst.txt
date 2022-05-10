Command-Line Tool
=================

The ``schema_markdown`` package can be used as a command like tool like so:

.. code-block:: sh

   $ schema-markdown --help
   usage: schema-markdown [-h] {compile,validate} ...

   positional arguments:
     {compile,validate}
       compile           Parse Schema Markdown files
       validate          Schema-validate JSON files

   options:
     -h, --help          show this help message and exit

The **compile** command compiles one or more :ref:`schema-markdown:Schema Markdown` files and
outputs a :ref:`type-model:Type Model` object:

.. code-block:: text

   usage: schema-markdown compile [-h] [-o PATH] [--referenced TYPE] [--compact]
                                  [schema ...]

   positional arguments:
     schema             Schema Markdown file paths. If none, default is stdin.

   options:
     -h, --help         show this help message and exit
     -o PATH            Optional JSON type model output file path. Default is
                        stdout.
     --referenced TYPE  Output only referenced types
     --compact          Generate compact JSON

The **validate** command parses a :ref:`schema-markdown:Schema Markdown` file and a type and
schema-validates one or more JSON files:

.. code-block:: text

   usage: schema-markdown validate [-h] -s SCHEMA -t TYPE [paths ...]

   positional arguments:
     paths       JSON file paths to validate. If none, defaults is stdin.

   options:
     -h, --help  show this help message and exit
     -s SCHEMA   Schema Markdown file path
     -t TYPE     Name of type to validate
