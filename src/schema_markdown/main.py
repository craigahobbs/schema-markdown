# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/master/LICENSE

"""
Schema Markdown compiler and schema validator tool
"""

import argparse
import json
import sys

from .parser import SchemaMarkdownParser
from .schema import validate_type


def main():
    """
    Schema Markdown compiler and schema validator tool main entry point
    """

    # Command line arguments
    arg_parser = argparse.ArgumentParser(prog='schema_markdown')
    subparsers = arg_parser.add_subparsers(required=True, dest='command')
    parser_compile = subparsers.add_parser('compile', help='Parse Schema Markdown files')
    parser_compile.add_argument('paths', nargs='*', help='Schema Markdown file paths. If none, default is stdin.')
    parser_compile.add_argument('-o', metavar='PATH', dest='output', help='Optional JSON type model output file path. Default is stdout.')
    parser_compile.add_argument('--title', help='The type model title')
    parser_compile.add_argument('--compact', action='store_true', help='Generate compact JSON')
    parser_validate = subparsers.add_parser('validate', help='Schema-validate JSON files')
    parser_validate.add_argument('schema', help='Schema Markdown file path')
    parser_validate.add_argument('type', help='Name of type to validate')
    parser_validate.add_argument('paths', nargs='*', help='JSON file paths to validate. If none, defaults is stdin.')
    args = arg_parser.parse_args()

    # Compile command?
    if args.command == 'compile':

        # Parse the Schema Markdown
        parser = SchemaMarkdownParser()
        if not args.paths:
            parser.parse(sys.stdin)
        else:
            for path in args.paths:
                with open(path, 'r') as schema_markdown_file:
                    parser.parse(schema_markdown_file, finalize=False)
            parser.finalize()

        # Create the type model with title
        type_model = {
            'title': args.title if args.title else 'Index',
            'types': parser.types
        }

        # Write the JSON
        json_encoder = json.JSONEncoder(indent=None if args.compact else 4, sort_keys=True)
        if args.output is not None:
            with open(args.output, 'w') as json_file:
                json_file.write(json_encoder.encode(type_model))
        else:
            sys.stdout.write(json_encoder.encode(type_model))

    # Validate command?
    else: # args.command == 'validate':

        # Parse the Schema Markdown (or use the type model)
        parser = SchemaMarkdownParser()
        parser.load(args.schema)

        # Validate the input JSON
        if not args.paths:
            validate_type(parser.types, args.type, json.load(sys.stdin))
        else:
            for path in args.paths:
                with open(path, 'r') as input_file:
                    validate_type(parser.types, args.type, json.load(input_file))
