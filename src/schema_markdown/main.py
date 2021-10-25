# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/main/LICENSE

"""
schema-markdown command-line script main module
"""

import argparse
import json
import sys

from .parser import SchemaMarkdownParser, SchemaMarkdownParserError
from .schema import get_referenced_types, validate_type


def main():
    """
    schema-markdown command-line script main entry point
    """

    # Command line arguments
    arg_parser = argparse.ArgumentParser(prog='schema-markdown')
    subparsers = arg_parser.add_subparsers(required=True, dest='command')
    parser_compile = subparsers.add_parser('compile', help='Parse Schema Markdown files')
    parser_compile.add_argument('schema', nargs='*', help='Schema Markdown file paths. If none, default is stdin.')
    parser_compile.add_argument('-o', metavar='PATH', dest='output', help='Optional JSON type model output file path. Default is stdout.')
    parser_compile.add_argument('-t', dest='title', help='The type model title')
    parser_compile.add_argument('--referenced', metavar='TYPE', action='append', help='Output only referenced types')
    parser_compile.add_argument('--compact', action='store_true', help='Generate compact JSON')
    parser_validate = subparsers.add_parser('validate', help='Schema-validate JSON files')
    parser_validate.add_argument('-s', dest='schema', required=True, action='append', help='Schema Markdown file path')
    parser_validate.add_argument('-t', dest='type', required=True, help='Name of type to validate')
    parser_validate.add_argument('paths', nargs='*', help='JSON file paths to validate. If none, defaults is stdin.')
    args = arg_parser.parse_args()

    # Parse the Schema Markdown
    parser = SchemaMarkdownParser()
    try:
        if not args.schema:
            parser.parse(sys.stdin)
        else:
            for path in args.schema:
                with open(path, 'r', encoding='utf-8') as schema_markdown_file:
                    parser.parse(schema_markdown_file, filename=path, finalize=False)
            parser.finalize()
    except SchemaMarkdownParserError as exc:
        arg_parser.exit(1, '\n'.join(exc.errors))
    types = parser.types

    # Compile command?
    if args.command == 'compile':

        # Get the referenced types
        if args.referenced is not None:
            referenced_types = {}
            for referenced_type in args.referenced:
                referenced_types.update(get_referenced_types(types, referenced_type))
            types = referenced_types

        # Create the type model with title
        type_model = {
            'title': args.title if args.title else 'Index',
            'types': types
        }

        # Write the JSON
        json_encoder = json.JSONEncoder(indent=None if args.compact else 4, sort_keys=True)
        if args.output is not None:
            with open(args.output, 'w', encoding='utf-8') as json_file:
                json_file.write(json_encoder.encode(type_model))
        else:
            sys.stdout.write(json_encoder.encode(type_model))

    # Validate command?
    else: # args.command == 'validate'

        # Validate the input JSON
        if not args.paths:
            validate_type(types, args.type, json.load(sys.stdin))
        else:
            for path in args.paths:
                with open(path, 'r', encoding='utf-8') as input_file:
                    validate_type(types, args.type, json.load(input_file))
