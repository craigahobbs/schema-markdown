# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/master/LICENSE

"""
schema-markdown schema type model
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from math import isnan, isinf
from uuid import UUID

from .schema_util import validate_type_model_types_errors
from .type_model import TYPE_MODEL


def get_referenced_types(types, type_name, referenced_types=None):
    """
    Get a type's referenced type model

    :param dict types: The map of user type name to user type model
    :param str type_name: The type name
    :param dict referenced_types: An optional map of referenced user type name to user type
    :returns: The map of referenced user type name to user type model
    """

    return _get_referenced_types(types, {'user': type_name}, referenced_types)


def _get_referenced_types(types, type_, referenced_types=None):

    # Create the referenced types dict, if necessary
    if referenced_types is None:
        referenced_types = {}

    # Array?
    if 'array' in type_:
        array = type_['array']
        _get_referenced_types(types, array['type'], referenced_types)

    # Dict?
    elif 'dict' in type_:
        dict_ = type_['dict']
        _get_referenced_types(types, dict_['type'], referenced_types)
        if 'keyType' in dict_:
            _get_referenced_types(types, dict_['keyType'], referenced_types)

    # User type?
    elif 'user' in type_:
        type_name = type_['user']

        # Already encountered?
        if type_name not in referenced_types:
            user_type = types[type_name]
            referenced_types[type_name] = user_type

            # Struct?
            if 'struct' in user_type:
                struct = user_type['struct']
                if 'bases' in struct:
                    for base in struct['bases']:
                        _get_referenced_types(types, {'user': base}, referenced_types)
                for member in get_struct_members(types, struct):
                    _get_referenced_types(types, member['type'], referenced_types)

            # Enum
            elif 'enum' in user_type:
                enum = user_type['enum']
                if 'bases' in enum:
                    for base in enum['bases']:
                        _get_referenced_types(types, {'user': base}, referenced_types)

            # Typedef?
            elif 'typedef' in user_type:
                typedef = user_type['typedef']
                _get_referenced_types(types, typedef['type'], referenced_types)

            # Action?
            elif 'action' in user_type: # pragma: no branch
                action = user_type['action']
                if 'path' in action:
                    _get_referenced_types(types, {'user': action['path']}, referenced_types)
                if 'query' in action:
                    _get_referenced_types(types, {'user': action['query']}, referenced_types)
                if 'input' in action:
                    _get_referenced_types(types, {'user': action['input']}, referenced_types)
                if 'output' in action:
                    _get_referenced_types(types, {'user': action['output']}, referenced_types)
                if 'errors' in action:
                    _get_referenced_types(types, {'user': action['errors']}, referenced_types)

    return referenced_types


class ValidationError(Exception):
    """
    schema-markdown type model validation error

    :param str msg: The error message
    :param member_fqn: The fully qualified member name or None
    :type member_fqn: str or None
    """

    __slots__ = ('member',)

    def __init__(self, msg, member_fqn=None):
        super().__init__(msg)

        #: The fully qualified member name or None
        self.member = member_fqn


def validate_type(types, type_name, value, member_fqn=None):
    """
    Type-validate a value using the schema-markdown user type model. Container values are duplicated
    since some member types are transformed during validation.

    :param dict types: The map of user type name to user type model
    :param str type_name: The type name
    :param object value: The value object to validate
    :param str member_fqn: The fully-qualified member name
    :returns: The validated, transformed value object
    :raises ValidationError: A validation error occurred
    """

    if type_name not in types:
        raise ValidationError(f"Unknown type {type_name!r}")
    return _validate_type(types, {'user': type_name}, value, member_fqn)


def _validate_type(types, type_, value, member_fqn=None):
    value_new = value

    # Built-in type?
    if 'builtin' in type_:
        builtin = type_['builtin']

        # string?
        if builtin == 'string':

            # Not a string?
            if not isinstance(value, str):
                raise _member_error(type_, value, member_fqn)

        # int?
        elif builtin == 'int':

            # Convert string, float, or Decimal?
            if isinstance(value, (str, float, Decimal)):
                try:
                    value_new = int(value)
                    if not isinstance(value, str) and value_new != value:
                        raise ValueError()
                except ValueError:
                    raise _member_error(type_, value, member_fqn) from None

            # Not an int?
            elif not isinstance(value, int) or isinstance(value, bool):
                raise _member_error(type_, value, member_fqn)

        # float?
        elif builtin == 'float':

            # Convert string, int, or Decimal?
            if isinstance(value, (str, int, Decimal)) and not isinstance(value, bool):
                try:
                    value_new = float(value)
                    if isnan(value_new) or isinf(value_new):
                        raise ValueError()
                except ValueError:
                    raise _member_error(type_, value, member_fqn) from None

            # Not a float?
            elif not isinstance(value, float):
                raise _member_error(type_, value, member_fqn)

        # bool?
        elif builtin == 'bool':

            # Convert string?
            if isinstance(value, str):
                if value == 'true':
                    value_new = True
                elif value == 'false':
                    value_new = False
                else:
                    raise _member_error(type_, value, member_fqn)

            # Not a bool?
            elif not isinstance(value, bool):
                raise _member_error(type_, value, member_fqn)

        # date?
        elif builtin == 'date':

            # Convert string?
            if isinstance(value, str):
                try:
                    value_new = datetime.fromisoformat(value).date()
                except ValueError:
                    raise _member_error(type_, value, member_fqn)

            # Not a date?
            elif not isinstance(value, date) or isinstance(value, datetime):
                raise _member_error(type_, value, member_fqn)

        # datetime?
        elif builtin == 'datetime':

            # Convert string?
            if isinstance(value, str):
                try:
                    value_new = datetime.fromisoformat(value)
                except ValueError:
                    raise _member_error(type_, value, member_fqn)

                # No timezone?
                if value_new.tzinfo is None:
                    value_new = value_new.replace(tzinfo=timezone.utc)

            # Not a datetime?
            elif not isinstance(value, datetime):
                raise _member_error(type_, value, member_fqn)

        # uuid?
        elif builtin == 'uuid':

            # Convert string?
            if isinstance(value, str):
                try:
                    value_new = UUID(value)
                except ValueError:
                    raise _member_error(type_, value, member_fqn)

            # Not a UUID?
            elif not isinstance(value, UUID):
                raise _member_error(type_, value, member_fqn)

    # array?
    elif 'array' in type_:

        # Valid value type?
        array = type_['array']
        array_type = array['type']
        array_attr = array.get('attr')
        if isinstance(value, str) and value == '':
            value_new = []
        elif not isinstance(value, (list, tuple)):
            raise _member_error(type_, value, member_fqn)

        # Validate the list contents
        value_copy = []
        array_value_nullable = array_attr is not None and 'nullable' in array_attr and array_attr['nullable']
        for ix_array_value, array_value in enumerate(value_new):
            member_fqn_value = f'{ix_array_value}' if member_fqn is None else f'{member_fqn}.{ix_array_value}'
            if array_value is None or (array_value_nullable and array_value == 'null'):
                array_value = None
            else:
                array_value = _validate_type(types, array_type, array_value, member_fqn_value)
            _validate_attr(array_type, array_attr, array_value, member_fqn_value)
            value_copy.append(array_value)

        # Return the validated, transformed copy
        value_new = value_copy

    # dict?
    elif 'dict' in type_:

        # Valid value type?
        dict_ = type_['dict']
        dict_type = dict_['type']
        dict_attr = dict_.get('attr')
        dict_key_type = dict_['keyType'] if 'keyType' in dict_ else {'builtin': 'string'}
        dict_key_attr = dict_.get('keyAttr')
        if isinstance(value, str) and value == '':
            value_new = {}
        elif not isinstance(value, dict):
            raise _member_error(type_, value, member_fqn)

        # Validate the dict key/value pairs
        value_copy = {}
        dict_key_nullable = dict_key_attr is not None and 'nullable' in dict_key_attr and dict_key_attr['nullable']
        dict_value_nullable = dict_attr is not None and 'nullable' in dict_attr and dict_attr['nullable']
        for dict_key, dict_value in value_new.items():
            member_fqn_key = dict_key if member_fqn is None else f'{member_fqn}.{dict_key}'

            # Validate the key
            if dict_key is None or (dict_key_nullable and dict_key == 'null'):
                dict_key = None
            else:
                dict_key = _validate_type(types, dict_key_type, dict_key, member_fqn)
            _validate_attr(dict_key_type, dict_key_attr, dict_key, member_fqn)

            # Validate the value
            if dict_value is None or (dict_value_nullable and dict_value == 'null'):
                dict_value = None
            else:
                dict_value = _validate_type(types, dict_type, dict_value, member_fqn_key)
            _validate_attr(dict_type, dict_attr, dict_value, member_fqn_key)

            # Copy the key/value
            value_copy[dict_key] = dict_value

        # Return the validated, transformed copy
        value_new = value_copy

    # User type?
    elif 'user' in type_:
        user_type = types[type_['user']]

        # action?
        if 'action' in user_type:
            raise _member_error(type_, value, member_fqn)

        # typedef?
        if 'typedef' in user_type:
            typedef = user_type['typedef']
            typedef_attr = typedef.get('attr')

            # Validate the value
            value_nullable = typedef_attr is not None and 'nullable' in typedef_attr and typedef_attr['nullable']
            if value is None or (value_nullable and value == 'null'):
                value_new = None
            else:
                value_new = _validate_type(types, typedef['type'], value, member_fqn)
            _validate_attr(type_, typedef_attr, value_new, member_fqn)

        # enum?
        elif 'enum' in user_type:
            enum = user_type['enum']

            # Not a valid enum value?
            if value not in (enum_value['name'] for enum_value in get_enum_values(types, enum)):
                raise _member_error(type_, value, member_fqn)

        # struct?
        elif 'struct' in user_type:
            struct = user_type['struct']

            # Valid value type?
            if isinstance(value, str) and value == '':
                value_new = {}
            elif not isinstance(value, dict):
                raise _member_error({'user': struct['name']}, value, member_fqn)

            # Valid union?
            is_union = struct.get('union', False)
            if is_union:
                if len(value) != 1:
                    raise _member_error({'user': struct['name']}, value, member_fqn)

            # Validate the struct members
            value_copy = {}
            for member in get_struct_members(types, struct):
                member_name = member['name']
                member_fqn_member = member_name if member_fqn is None else f'{member_fqn}.{member_name}'
                member_optional = member.get('optional', False)

                # Missing non-optional member?
                if member_name not in value_new:
                    if not member_optional and not is_union:
                        raise ValidationError(f"Required member {member_fqn_member!r} missing")
                else:
                    # Validate the member value
                    member_value = value_new[member_name]
                    if member_value is not None:
                        member_value = _validate_type(types, member['type'], member_value, member_fqn_member)
                    _validate_attr(member['type'], member.get('attr'), member_value, member_fqn_member)

                    # Copy the validated member
                    value_copy[member_name] = member_value

            # Any unknown members?
            if len(value_copy) != len(value_new):
                member_set = {member['name'] for member in get_struct_members(types, struct)}
                unknown_key = next(value_name for value_name in value_new.keys() if value_name not in member_set) # pragma: no branch
                unknown_fqn = unknown_key if member_fqn is None else f'{member_fqn}.{unknown_key}'
                raise ValidationError(f"Unknown member {unknown_fqn!r:.100s}")

            # Return the validated, transformed copy
            value_new = value_copy

    return value_new


def _member_error(type_, value, member_fqn, attr=None):
    member_part = f" for member {member_fqn!r}" if member_fqn else ''
    type_name = type_['builtin'] if 'builtin' in type_ else (
        'array' if 'array' in type_ else ('dict' if 'dict' in type_ else type_['user']))
    attr_part = f' [{attr}]' if attr else ''
    msg = f"Invalid value {value!r:.1000s} (type {value.__class__.__name__!r}){member_part}, expected type {type_name!r}{attr_part}"
    return ValidationError(msg, member_fqn)


def _validate_attr(type_, attr, value, member_fqn):
    if value is None:
        value_nullable = attr is not None and 'nullable' in attr and attr['nullable']
        if not value_nullable:
            raise _member_error(type_, value, member_fqn)
    elif attr is not None:
        if 'eq' in attr and not value == attr['eq']:
            raise _member_error(type_, value, member_fqn, f'== {attr["eq"]}')
        if 'lt' in attr and not value < attr['lt']:
            raise _member_error(type_, value, member_fqn, f'< {attr["lt"]}')
        if 'lte' in attr and not value <= attr['lte']:
            raise _member_error(type_, value, member_fqn, f'<= {attr["lte"]}')
        if 'gt' in attr and not value > attr['gt']:
            raise _member_error(type_, value, member_fqn, f'> {attr["gt"]}')
        if 'gte' in attr and not value >= attr['gte']:
            raise _member_error(type_, value, member_fqn, f'>= {attr["gte"]}')
        if 'lenEq' in attr and not len(value) == attr['lenEq']:
            raise _member_error(type_, value, member_fqn, f'len == {attr["lenEq"]}')
        if 'lenLT' in attr and not len(value) < attr['lenLT']:
            raise _member_error(type_, value, member_fqn, f'len < {attr["lenLT"]}')
        if 'lenLTE' in attr and not len(value) <= attr['lenLTE']:
            raise _member_error(type_, value, member_fqn, f'len <= {attr["lenLTE"]}')
        if 'lenGT' in attr and not len(value) > attr['lenGT']:
            raise _member_error(type_, value, member_fqn, f'len > {attr["lenGT"]}')
        if 'lenGTE' in attr and not len(value) >= attr['lenGTE']:
            raise _member_error(type_, value, member_fqn, f'len >= {attr["lenGTE"]}')


def get_struct_members(types, struct):
    """
    Iterate the struct's members (inherited members first)

    :param dict types: The map of user type name to user type model
    :param dict struct: The struct model
    :returns: The array of struct member models
    """

    if 'bases' in struct:
        for base in struct['bases']:
            base_user_type = types[base]
            while 'typedef' in base_user_type:
                base_user_type = types[base_user_type['typedef']['type']['user']]
            yield from get_struct_members(types, base_user_type['struct'])
    if 'members' in struct:
        yield from struct['members']


def get_enum_values(types, enum):
    """
    Iterate the enum's values (inherited values first)

    :param dict types: The map of user type name to user type model
    :param dict enum: The enum model
    :returns: The array of enum value models
    """

    if 'bases' in enum:
        for base in enum['bases']:
            base_user_type = types[base]
            while 'typedef' in base_user_type:
                base_user_type = types[base_user_type['typedef']['type']['user']]
            yield from get_enum_values(types, base_user_type['enum'])
    if 'values' in enum:
        yield from enum['values']


def validate_type_model_types(types):
    """
    Validate a user type model's types

    :param dict types: The map of user type name to user type model
    :returns: The validated, transformed type-model types dict
    :raises ValidationError: A validation error occurred
    """

    # Validate with the type model
    validated_types = validate_type(TYPE_MODEL['types'], 'Types', types)

    # Do additional type model validation
    errors = validate_type_model_types_errors(validated_types)
    if errors:
        raise ValidationError('\n'.join(message for _, _, message in sorted(errors)))

    return validated_types


def validate_type_model(type_model):
    """
    Validate a user type model

    :param dict type_model: The user type model
    :returns: The validated, transformed type model
    :raises ValidationError: A validation error occurred
    """

    # Validate with the type model
    validated_type_model = validate_type(TYPE_MODEL['types'], 'TypeModel', type_model)

    # Do additional type model validation
    errors = validate_type_model_types_errors(validated_type_model['types'])
    if errors:
        raise ValidationError('\n'.join(message for _, _, message in sorted(errors)))

    return validated_type_model
