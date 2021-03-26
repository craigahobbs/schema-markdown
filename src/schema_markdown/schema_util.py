# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/master/LICENSE

"""
schema-markdown schema type model utilities
"""


def validate_type_model_types_errors(types):
    """
    Validate a user type model's types

    :param dict types: The map of user type name to user type model
    :returns: The list of type name, member name, and error message tuples
    """

    errors = []

    # Check each user type
    for type_name, user_type in types.items():

        # Struct?
        if 'struct' in user_type:
            struct = user_type['struct']

            # Inconsistent type name?
            if type_name != struct['name']:
                errors.append((type_name, None, f'Inconsistent type name {struct["name"]!r} for {type_name!r}'))

            # Check base types
            if 'bases' in struct:
                is_union = struct.get('union', False)
                for base_name in struct['bases']:
                    invalid_base = True
                    base_user_type = _get_effective_user_type(types, base_name)
                    if base_user_type is not None and 'struct' in base_user_type:
                        if is_union == base_user_type['struct'].get('union', False):
                            invalid_base = False
                    if invalid_base:
                        errors.append((type_name, None, f'Invalid struct base type {base_name!r}'))

            # Iterate the members
            try:
                members = set()
                for member in _get_struct_members(types, struct, set()):
                    member_name = member['name']

                    # Duplicate member?
                    if member_name not in members:
                        members.add(member_name)
                    else:
                        errors.append((type_name, member_name, f'Redefinition of {type_name!r} member {member_name!r}'))

                    # Check member type and attributes
                    _validate_type_model_type(errors, types, member['type'], member.get('attr'), struct['name'], member['name'])

            except ValueError:
                errors.append((type_name, None, f'Circular base type detected for type {type_name!r}'))

        # Enum?
        elif 'enum' in user_type:
            enum = user_type['enum']

            # Inconsistent type name?
            if type_name != enum['name']:
                errors.append((type_name, None, f'Inconsistent type name {enum["name"]!r} for {type_name!r}'))

            # Check base types
            if 'bases' in enum:
                for base_name in enum['bases']:
                    base_user_type = _get_effective_user_type(types, base_name)
                    if base_user_type is None or 'enum' not in base_user_type:
                        errors.append((type_name, None, f'Invalid enum base type {base_name!r}'))

            # Get the enumeration values
            try:
                values = set()
                for value in _get_enum_values(types, enum, set()):
                    value_name = value['name']

                    # Duplicate value?
                    if value_name not in values:
                        values.add(value_name)
                    else:
                        errors.append((type_name, value_name, f'Redefinition of {type_name!r} value {value_name!r}'))

            except ValueError:
                errors.append((type_name, None, f'Circular base type detected for type {type_name!r}'))

        # Typedef?
        elif 'typedef' in user_type:
            typedef = user_type['typedef']

            # Inconsistent type name?
            if type_name != typedef['name']:
                errors.append((type_name, None, f'Inconsistent type name {typedef["name"]!r} for {type_name!r}'))

            # Check the type and its attributes
            _validate_type_model_type(errors, types, typedef['type'], typedef.get('attr'), type_name, None)

        # Action?
        elif 'action' in user_type: # pragma: no branch
            action = user_type['action']

            # Inconsistent type name?
            if type_name != action['name']:
                errors.append((type_name, None, f'Inconsistent type name {action["name"]!r} for {type_name!r}'))

            # Check action section types
            for section in ('path', 'query', 'input', 'output', 'errors'):
                if section in action:
                    section_type_name = action[section]

                    # Check the section type
                    _validate_type_model_type(errors, types, {'user': section_type_name}, None, type_name, None)

            # Compute effective input member counts
            member_sections = {}
            for section in ('path', 'query', 'input'):
                if section in action:
                    section_type_name = action[section]
                    if section_type_name in types:
                        section_user_type = _get_effective_user_type(types, section_type_name)
                        if section_user_type is not None and 'struct' in section_user_type:
                            section_struct = section_user_type['struct']

                            # Get the section struct's members and count member occurrences
                            try:
                                for member in _get_struct_members(types, section_struct, set()):
                                    member_name = member['name']
                                    if member_name not in member_sections:
                                        member_sections[member_name] = []
                                    member_sections[member_name].append(section_struct['name'])
                            except ValueError:
                                pass

            # Check for duplicate input members
            for member_name, member_section_names in member_sections.items():
                if len(member_section_names) > 1:
                    for section_type in member_section_names:
                        errors.append((section_type, member_name, f'Redefinition of {section_type!r} member {member_name!r}'))

    return errors


def _get_effective_type(types, type_):
    if 'user' in type_ and type_['user'] in types:
        user_type = types[type_['user']]
        if 'typedef' in user_type:
            return _get_effective_type(types, user_type['typedef']['type'])
    return type_


def _get_effective_user_type(types, user_type_name):
    user_type = types.get(user_type_name)
    if user_type is not None and 'typedef' in user_type:
        type_effective = _get_effective_type(types, user_type['typedef']['type'])
        if 'user' not in type_effective:
            return None
        return types.get(type_effective['user'])
    return user_type


def _get_struct_members(types, struct, visited=None):
    yield from _get_type_items(types, struct, visited, 'struct', 'members')


def _get_enum_values(types, enum, visited=None):
    yield from _get_type_items(types, enum, visited, 'enum', 'values')


def _get_type_items(types, type_, visited, def_name, member_name):
    if 'bases' in type_:
        for base in type_['bases']:
            user_type = _get_effective_user_type(types, base)
            if user_type is not None and def_name in user_type:
                user_type_name = user_type[def_name]['name']
                if user_type_name not in visited:
                    visited.add(user_type_name)
                    yield from _get_type_items(types, user_type[def_name], visited, def_name, member_name)
                else:
                    raise ValueError()
    if member_name in type_:
        yield from type_[member_name]


# Map of attribute struct member name to attribute description
_ATTR_TO_TEXT = {
    'eq': '==',
    'lt': '<',
    'lte': '<=',
    'gt': '>',
    'gte': '>=',
    'lenEq': 'len ==',
    'lenLT': 'len <',
    'lenLTE': 'len <=',
    'lenGT': 'len >',
    'lenGTE': 'len >='
}


# Map of type name to valid attribute set
_TYPE_TO_ALLOWED_ATTR = {
    'float': set(['eq', 'lt', 'lte', 'gt', 'gte']),
    'int': set(['eq', 'lt', 'lte', 'gt', 'gte']),
    'string': set(['lenEq', 'lenLT', 'lenLTE', 'lenGT', 'lenGTE']),
    'array': set(['lenEq', 'lenLT', 'lenLTE', 'lenGT', 'lenGTE']),
    'dict': set(['lenEq', 'lenLT', 'lenLTE', 'lenGT', 'lenGTE'])
}


def _validate_type_model_type(errors, types, type_, attr, type_name, member_name):

    # Helper function to push an error tuple
    def error(message):
        if member_name is not None:
            errors.append((type_name, member_name, f'{message} from {type_name!r} member {member_name!r}'))
        else:
            errors.append((type_name, None, f'{message} from {type_name!r}'))

    # Array?
    if 'array' in type_:
        array = type_['array']

        # Check the type and its attributes
        array_type = _get_effective_type(types, array['type'])
        _validate_type_model_type(errors, types, array_type, array.get('attr'), type_name, member_name)

    # Dict?
    elif 'dict' in type_:
        dict_ = type_['dict']

        # Check the type and its attributes
        dict_type = _get_effective_type(types, dict_['type'])
        _validate_type_model_type(errors, types, dict_type, dict_.get('attr'), type_name, member_name)

        # Check the dict key type and its attributes
        if 'keyType' in dict_:
            dict_key_type = _get_effective_type(types, dict_['keyType'])
            _validate_type_model_type(errors, types, dict_key_type, dict_.get('keyAttr'), type_name, member_name)

            # Valid dict key type (string or enum)
            if not ('builtin' in dict_key_type and dict_key_type['builtin'] == 'string') and \
               not ('user' in dict_key_type and dict_key_type['user'] in types and 'enum' in types[dict_key_type['user']]):
                error('Invalid dictionary key type')

    # User type?
    elif 'user' in type_:
        user_type_name = type_['user']

        # Unknown user type?
        if user_type_name not in types:
            error(f'Unknown type {user_type_name!r}')
        else:
            user_type = types[user_type_name]

            # Action type references not allowed
            if 'action' in user_type:
                error(f'Invalid reference to action {user_type_name!r}')

    # Any not-allowed attributes?
    if attr is not None:
        type_effective = _get_effective_type(types, type_)
        type_key = next(iter(type_effective.keys()), None)
        allowed_attr = _TYPE_TO_ALLOWED_ATTR.get(type_effective[type_key] if type_key == 'builtin' else type_key)
        disallowed_attr = set(attr)
        disallowed_attr.discard('nullable')
        if allowed_attr is not None:
            disallowed_attr -= allowed_attr
        if disallowed_attr:
            for attr_key in disallowed_attr:
                attr_value = f'{attr[attr_key]:.6f}'.rstrip('0').rstrip('.')
                attr_text = f'{_ATTR_TO_TEXT[attr_key]} {attr_value}'
                error(f'Invalid attribute {attr_text!r}')
