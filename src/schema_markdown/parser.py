# Licensed under the MIT License
# https://github.com/craigahobbs/schema_markdown/blob/main/LICENSE

"""
Schema Markdown parser
"""

from itertools import chain
import re

from .schema_util import validate_type_model_errors


# Built-in types
BUILTIN_TYPES = {'bool', 'date', 'datetime', 'float', 'int', 'object', 'string', 'uuid'}


# Schema Markdown regex
RE_PART_ID = r'(?:[A-Za-z]\w*)'
RE_PART_ATTR_GROUP = \
    r'(?:(?P<nullable>nullable)' \
    r'|(?P<op><=|<|>|>=|==)\s*(?P<opnum>-?\d+(?:\.\d+)?)' \
    r'|(?P<ltype>len)\s*(?P<lop><=|<|>|>=|==)\s*(?P<lopnum>\d+))'
RE_PART_ATTR = re.sub(r'\(\?P<[^>]+>', r'(?:', RE_PART_ATTR_GROUP)
RE_PART_ATTRS = r'(?:' + RE_PART_ATTR + r'(?:\s*,\s*' + RE_PART_ATTR + r')*)'
RE_ATTR_GROUP = re.compile(RE_PART_ATTR_GROUP)
RE_FIND_ATTRS = re.compile(RE_PART_ATTR + r'(?:\s*,\s*|\s*\Z)')
RE_LINE_CONT = re.compile(r'\\s*$')
RE_COMMENT = re.compile(r'^\s*(?:#-.*|#(?P<doc>.*))?$')
RE_GROUP = re.compile(r'^group(?:\s+"(?P<group>.+?)")?\s*$')
RE_ACTION = re.compile(r'^action\s+(?P<id>' + RE_PART_ID + r')')
RE_PART_BASE_IDS = r'(?:\s*\(\s*(?P<base_ids>' + RE_PART_ID + r'(?:\s*,\s*' + RE_PART_ID + r')*)\s*\)\s*)'
RE_BASE_IDS_SPLIT = re.compile(r'\s*,\s*')
RE_DEFINITION = re.compile(r'^(?P<type>struct|union|enum)\s+(?P<id>' + RE_PART_ID + r')' + RE_PART_BASE_IDS + r'?\s*$')
RE_SECTION = re.compile(r'^\s+(?P<type>path|query|input|output|errors)' + RE_PART_BASE_IDS + r'?\s*$')
RE_SECTION_PLAIN = re.compile(r'^\s+(?P<type>urls)\s*$')
RE_PART_TYPEDEF = \
    r'(?P<type>' + RE_PART_ID + r')' \
    r'(?:\s*\(\s*(?P<attrs>' + RE_PART_ATTRS + r')\s*\))?' \
    r'(?:' \
    r'(?:\s*\[\s*(?P<array>' + RE_PART_ATTRS + r'?)\s*\])?' \
    r'|' \
    r'(?:' \
    r'\s*:\s*(?P<dictValueType>' + RE_PART_ID + r')' \
    r'(?:\s*\(\s*(?P<dictValueAttrs>' + RE_PART_ATTRS + r')\s*\))?' \
    r')?' \
    r'(?:\s*\{\s*(?P<dict>' + RE_PART_ATTRS + r'?)\s*\})?' \
    r')' \
    r'\s+(?P<id>' + RE_PART_ID + r')'
RE_TYPEDEF = re.compile(r'^typedef\s+' + RE_PART_TYPEDEF + r'\s*$')
RE_MEMBER = re.compile(r'^\s+(?P<optional>optional\s+)?' + RE_PART_TYPEDEF + r'\s*$')
RE_VALUE = re.compile(r'^\s+(?P<id>' + RE_PART_ID + r')\s*$')
RE_VALUE_QUOTED = re.compile(r'^\s+"(?P<id>.*?)"\s*$')
RE_URL = re.compile(r'^\s+(?P<method>[A-Za-z]+|\*)(?:\s+(?P<path>/[^\s]*))?')


def parse_schema_markdown(text, types=None, filename='', validate=True):
    """
    Parse Schema Markdown from a string or an iterator of strings

    :param text: The Schema Markdown text
    :type text: str or ~collections.abc.Iterable(str)
    :param object types: The `type model <https://craigahobbs.github.io/schema-markdown-doc/doc/#var.vName='Types'>`__
    :param str filename: The name of file being parsed (for error messages)
    :param bool validate: If True, validate after parsing
    :returns: The `type model <https://craigahobbs.github.io/schema-markdown-doc/doc/#var.vName='Types'>`__
    :raises SchemaMarkdownParserError: A parsing error occurred
    """

    # Current parser state
    if types is None:
        types = {}
    error_map = {}
    filepos = {}
    action = None
    urls = None
    user_type = None
    doc = []
    doc_group = None
    linenum = 0

    # Helper function to add an error message
    def add_error(msg, error_filename, error_linenum):
        error_msg = f'{error_filename}:{error_linenum}: error: {msg}'
        error_map[error_msg] = (error_filename, error_linenum, error_msg)

    # Helper function to get documentation strings
    def get_doc():
        nonlocal doc
        result = None
        if doc:
            result = doc
            doc = []
        return result

    # Line-split all script text
    if isinstance(text, str):
        lines = text.splitlines()
    else:
        lines = list(chain.from_iterable(text_part.splitlines() for text_part in text))
    lines.append('')

    # Process each line
    line_continuation = []
    for line_part in lines:
        linenum += 1

        # Line continuation?
        line_part_no_continuation = RE_LINE_CONT.sub('', line_part)
        if line_continuation or line_part_no_continuation is not line_part:
            line_continuation.append(line_part_no_continuation)
        if line_part_no_continuation is not line_part:
            continue
        if line_continuation:
            line = ''.join(line_continuation)
            del line_continuation[:]
        else:
            line = line_part

        # Match syntax
        match_name, match = 'comment', RE_COMMENT.search(line)
        if match is None:
            match_name, match = 'group', RE_GROUP.search(line)
        if match is None:
            match_name, match = 'action', RE_ACTION.search(line)
        if match is None:
            match_name, match = 'definition', RE_DEFINITION.search(line)
        if match is None and action is not None:
            match_name, match = 'section', RE_SECTION.search(line)
        if match is None and action is not None:
            match_name, match = 'section_plain', RE_SECTION_PLAIN.search(line)
        if match is None and user_type is not None and 'enum' in user_type:
            match_value = RE_VALUE.search(line)
            if match_value is not None:
                match_name, match = 'value', match_value
            else:
                match_name, match = 'value', RE_VALUE_QUOTED.search(line)
        if match is None and user_type is not None and 'struct' in user_type:
            match_name, match = 'member', RE_MEMBER.search(line)
        if match is None and urls is not None:
            match_name, match = 'urls', RE_URL.search(line)
        if match is None:
            match_name, match = 'typedef', RE_TYPEDEF.search(line)
        if match is None:
            match_name = None

        # Comment?
        if match_name == 'comment':
            doc_string = match.group('doc')
            if doc_string is not None:
                doc.append(doc_string if not doc_string.startswith(' ') else doc_string[1:])

        # Documentation group?
        elif match_name == 'group':
            doc_group = match.group('group')
            if doc_group is not None:
                doc_group = doc_group.strip()
            else:
                doc_group = None

        # Action?
        elif match_name == 'action':
            action_id = match.group('id')

            # Action already defined?
            if action_id in types:
                add_error(f"Redefinition of action '{action_id}'", filename, linenum)

            # Clear parser state
            urls = None
            user_type = None
            action_doc = get_doc()

            # Create the new action
            action = {'name': action_id}
            types[action_id] = {'action': action}
            if action_doc is not None:
                action['doc'] = action_doc
            if doc_group is not None:
                action['docGroup'] = doc_group

        # Definition?
        elif match_name == 'definition':
            definition_string = match.group('type')
            definition_id = match.group('id')
            definition_base_ids = match.group('base_ids')

            # Type already defined?
            if definition_id in BUILTIN_TYPES or definition_id in types:
                add_error(f"Redefinition of type '{definition_id}'", filename, linenum)

            # Clear parser state
            action = None
            urls = None
            definition_doc = get_doc()

            # Struct definition
            if definition_string in ('struct', 'union'):

                # Create the new struct type
                struct = {'name': definition_id}
                user_type = types[definition_id] = {'struct': struct}
                if definition_doc is not None:
                    struct['doc'] = definition_doc
                if doc_group is not None:
                    struct['docGroup'] = doc_group
                if definition_string == 'union':
                    struct['union'] = True
                if definition_base_ids is not None:
                    struct['bases'] = RE_BASE_IDS_SPLIT.split(definition_base_ids)

            # Enum definition
            else:  # definition_string == 'enum':

                # Create the new enum type
                enum = {'name': definition_id}
                user_type = types[definition_id] = {'enum': enum}
                if definition_doc is not None:
                    enum['doc'] = definition_doc
                if doc_group is not None:
                    enum['docGroup'] = doc_group
                if definition_base_ids is not None:
                    enum['bases'] = RE_BASE_IDS_SPLIT.split(definition_base_ids)

            # Record finalization information
            filepos[definition_id] = linenum

        # Action section?
        elif match_name == 'section':
            section_string = match.group('type')
            section_base_ids = match.group('base_ids')

            # Action section redefinition?
            if section_string in action:
                add_error(f'Redefinition of action {section_string}', filename, linenum)

            # Clear parser state
            urls = None

            # Set the action section type
            section_type_name = f'{action["name"]}_{section_string}'
            action[section_string] = section_type_name
            if section_string == 'errors':
                enum = {'name': section_type_name}
                user_type = types[section_type_name] = {'enum': enum}
                if section_base_ids is not None:
                    enum['bases'] = RE_BASE_IDS_SPLIT.split(section_base_ids)
            else:
                struct = {'name': section_type_name}
                user_type = types[section_type_name] = {'struct': struct}
                if section_base_ids is not None:
                    struct['bases'] = RE_BASE_IDS_SPLIT.split(section_base_ids)

            # Record finalization information
            filepos[section_type_name] = linenum

        # Plain action section?
        elif match_name == 'section_plain':
            section_string = match.group('type')

            # Action section redefinition?
            if section_string in action:
                add_error(f'Redefinition of action {section_string}', filename, linenum)

            # Clear parser state
            user_type = None

            # Update the parser state
            urls = []

        # Enum value?
        elif match_name == 'value':
            value_string = match.group('id')

            # Add the enum value
            enum = user_type['enum']
            if 'values' not in enum:
                enum['values'] = []
            enum_value = {'name': value_string}
            enum['values'].append(enum_value)
            enum_value_doc = get_doc()
            if enum_value_doc is not None:
                enum_value['doc'] = enum_value_doc

            # Record finalization information
            filepos[f'{enum["name"]}.{value_string}'] = linenum

        # Struct member?
        elif match_name == 'member':
            optional = match.group('optional') is not None
            member_name = match.group('id')

            # Add the member
            struct = user_type['struct']
            if 'members' not in struct:
                struct['members'] = []
            member_type, member_attr = _parse_typedef(match)
            member_doc = get_doc()
            member = {
                'name': member_name,
                'type': member_type
            }
            struct['members'].append(member)
            if member_attr is not None:
                member['attr'] = member_attr
            if member_doc is not None:
                member['doc'] = member_doc
            if optional:
                member['optional'] = True

            # Record finalization information
            filepos[f'{struct["name"]}.{member_name}'] = linenum

        # URL?
        elif match_name == 'urls':
            method = match.group('method')
            path = match.group('path')

            # Create the action URL object
            action_url = {}
            if method != '*':
                action_url['method'] = method
            if path is not None:
                action_url['path'] = path

            # Duplicate URL?
            if action_url in urls:
                add_error(f'Duplicate URL: {method} {"" if path is None else path}', filename, linenum)

            # Add the URL
            if 'urls' not in action:
                action['urls'] = urls
            urls.append(action_url)

        # Typedef?
        elif match_name == 'typedef':
            definition_id = match.group('id')

            # Type already defined?
            if definition_id in BUILTIN_TYPES or definition_id in types:
                add_error(f"Redefinition of type '{definition_id}'", filename, linenum)

            # Clear parser state
            action = None
            urls = None
            user_type = None
            typedef_doc = get_doc()

            # Create the typedef
            typedef_type, typedef_attr = _parse_typedef(match)
            typedef = {
                'name': definition_id,
                'type': typedef_type
            }
            types[definition_id] = {'typedef': typedef}
            if typedef_attr is not None:
                typedef['attr'] = typedef_attr
            if typedef_doc is not None:
                typedef['doc'] = typedef_doc
            if doc_group is not None:
                typedef['docGroup'] = doc_group

            # Record finalization information
            filepos[definition_id] = linenum

        # Unrecognized line syntax
        else:
            add_error('Syntax error', filename, linenum)

    # Validate the type model, if requested
    if validate:
        for type_name, member_name, error_msg in validate_type_model_errors(types):
            error_filename = filename
            error_linenum = None
            if member_name is not None:
                error_linenum = filepos.get(f'{type_name}.{member_name}')
            if error_linenum is None:
                error_linenum = filepos.get(type_name)
            if error_linenum is None:
                error_filename = ''
                error_linenum = 1
            add_error(error_msg, error_filename, error_linenum)

    # Raise a parser exception if there are any errors
    errors = [msg for _, _, msg in sorted(error_map.values())]
    if errors:
        raise SchemaMarkdownParserError(errors)

    return types


# Helper function to parse a typedef - returns a type-model and attributes-model tuple
def _parse_typedef(match_typedef):
    array_attrs_string = match_typedef.group('array')
    dict_attrs_string = match_typedef.group('dict')

    # Array type?
    if array_attrs_string is not None:
        value_type_name = match_typedef.group('type')
        value_attr = _parse_attr(match_typedef.group('attrs'))
        array_type = {'type': _create_type(value_type_name)}
        if value_attr is not None:
            array_type['attr'] = value_attr
        return {'array': array_type}, _parse_attr(array_attrs_string)

    # Dictionary type?
    if dict_attrs_string is not None:
        value_type_name = match_typedef.group('dictValueType')
        if value_type_name is not None:
            value_attr = _parse_attr(match_typedef.group('dictValueAttrs'))
            key_type_name = match_typedef.group('type')
            key_attr = _parse_attr(match_typedef.group('attrs'))
            dict_type = {
                'type': _create_type(value_type_name),
                'keyType': _create_type(key_type_name)
            }
            if value_attr is not None:
                dict_type['attr'] = value_attr
            if key_attr is not None:
                dict_type['keyAttr'] = key_attr
        else:
            value_type_name = match_typedef.group('type')
            value_attr = _parse_attr(match_typedef.group('attrs'))
            dict_type = {'type': _create_type(value_type_name)}
            if value_attr is not None:
                dict_type['attr'] = value_attr
        return {'dict': dict_type}, _parse_attr(dict_attrs_string)

    # Non-container type...
    member_type_name = match_typedef.group('type')
    return _create_type(member_type_name), _parse_attr(match_typedef.group('attrs'))


# Helper function to create a type model
def _create_type(type_name):
    if type_name in BUILTIN_TYPES:
        return {'builtin': type_name}
    return {'user': type_name}


# Helper function to parse an attributes string - returns an attributes model
def _parse_attr(attrs_string):
    attrs = None
    if attrs_string is not None:
        for attr_string in RE_FIND_ATTRS.findall(attrs_string):
            if attrs is None:
                attrs = {}
            match_attr = RE_ATTR_GROUP.match(attr_string)
            attr_op = match_attr.group('op')
            attr_length_op = match_attr.group('lop') if attr_op is None else None

            if match_attr.group('nullable') is not None:
                attrs['nullable'] = True
            elif attr_op is not None:
                attr_value = float(match_attr.group('opnum'))
                if attr_op == '<':
                    attrs['lt'] = attr_value
                elif attr_op == '<=':
                    attrs['lte'] = attr_value
                elif attr_op == '>':
                    attrs['gt'] = attr_value
                elif attr_op == '>=':
                    attrs['gte'] = attr_value
                else:  # ==
                    attrs['eq'] = attr_value
            else:  # attr_length_op is not None:
                attr_value = int(match_attr.group('lopnum'))
                if attr_length_op == '<':
                    attrs['lenLT'] = attr_value
                elif attr_length_op == '<=':
                    attrs['lenLTE'] = attr_value
                elif attr_length_op == '>':
                    attrs['lenGT'] = attr_value
                elif attr_length_op == '>=':
                    attrs['lenGTE'] = attr_value
                else:  # ==
                    attrs['lenEq'] = attr_value
    return attrs


class SchemaMarkdownParserError(Exception):
    """
    Schema Markdown parser exception

    :param list(str) errors: The list of error strings
    """

    __slots__ = ('errors',)

    def __init__(self, errors):
        super().__init__('\n'.join(errors))

        #: The list of error strings
        self.errors = errors
