# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/main/LICENSE

"""
Encoding and decoding utilities
"""

from datetime import date, datetime, timezone
from decimal import Decimal
import json
from urllib.parse import quote, unquote
from uuid import UUID


class JSONEncoder(json.JSONEncoder):
    """
    A :class:`~json.JSONEncoder` sub-class with support for :class:`~datetime.datetime`, :class:`~datetime.date`,
    :class:`~decimal.Decimal`, and :class:`~uuid.UUID` objects.
    """

    __slots__ = ()

    def default(self, o):
        """
        The override of the :meth:`~json.JSONEncoder.default` method to add support for :class:`~datetime.datetime`,
        :class:`~datetime.date`, :class:`~decimal.Decimal`, and :class:`~uuid.UUID` objects.
        """

        if isinstance(o, datetime):
            return (o if o.tzinfo else o.replace(tzinfo=timezone.utc)).isoformat()
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, UUID):
            return f'{o}'
        return json.JSONEncoder.default(self, o)


def encode_query_string(obj, encoding='utf-8'):
    """
    Encode an object as a query string. Dictionaries, lists, and tuples are recursed. Each member key is expressed in
    fully-qualified form. List keys are the index into the list, and are in order. For example:

    >>> schema_markdown.encode_query_string({'a': 5, 'b': 3.14, 'c': {'d': 'foo', 'e': [1, 2, 3]}, 'f': [{'g': True}, {'g': False}]})
    'a=5&b=3.14&c.d=foo&c.e.0=1&c.e.1=2&c.e.2=3&f.0.g=true&f.1.g=false'

    :param object obj: The object to encode as a query string
    :param str encoding: The query string encoding
    :returns: The encoded query string
    """

    return '&'.join(f'{v}' if k is None else f'{k}={v}' for k, v in _encode_query_string_items(obj, None, encoding))


def _encode_query_string_items(obj, parent, encoding):
    if isinstance(obj, dict):
        if obj:
            for member, value in sorted(obj.items()):
                member_quoted = quote(f'{member}', encoding=encoding)
                parent_member = f'{parent}.{member_quoted}' if parent else member_quoted
                yield from _encode_query_string_items(value, parent_member, encoding)
        elif parent:
            yield parent, ''
    elif isinstance(obj, (list, tuple)):
        if obj:
            for idx, value in enumerate(obj):
                parent_member = f'{parent}.{idx}' if parent else f'{idx}'
                yield from _encode_query_string_items(value, parent_member, encoding)
        elif parent:
            yield parent, ''
    else:
        if isinstance(obj, bool):
            yield parent, 'true' if obj else 'false' # quote safe
        elif isinstance(obj, int):
            yield parent, f'{obj}' # quote safe
        elif isinstance(obj, datetime):
            if not obj.tzinfo:
                obj = obj.replace(tzinfo=timezone.utc)
            yield parent, quote(obj.isoformat(), encoding=encoding)
        elif isinstance(obj, date):
            yield parent, obj.isoformat() # quote safe
        elif isinstance(obj, UUID):
            yield parent, f'{obj}' # quote safe
        elif obj is None:
            yield parent, 'null'
        else: # str, float
            yield parent, quote(f'{obj}', encoding=encoding)


def decode_query_string(query_string, encoding='utf-8'):
    """
    Decode an object from a query string. Each member key of the query string is expressed in fully-qualified
    form. List keys are the index into the list, must be in order. For example:

    >>> schema_markdown.decode_query_string('a=5&b=3.14&c.d=foo&c.e.0=1&c.e.1=2&c.e.2=3&f.0.g=true&f.1.g=false')
    {'a': '5', 'b': '3.14', 'c': {'d': 'foo', 'e': ['1', '2', '3']}, 'f': [{'g': 'true'}, {'g': 'false'}]}

    :param str query_string: The query string
    :param str encoding: The query string encoding
    :returns: The decoded object
    :raises ValueError: Query string is invalid
    """

    # Build the object
    result = [None]
    for key_value in (key_value_str.split('=') for key_value_str in query_string.split('&') if key_value_str):

        # Split the key/value string
        try:
            key_str, value_str = key_value
            value = unquote(value_str, encoding=encoding) if encoding else value_str
        except ValueError:
            raise ValueError(f"Invalid key/value pair {'='.join(key_value)!r:.100s}")

        # Find/create the object on which to set the value
        parent = result
        key_parent = 0
        for key in (unquote(key, encoding=encoding) if encoding else key for key in key_str.split('.')):
            obj = parent[key_parent]

            # Array key?  First "key" of an array must start with "0".
            if isinstance(obj, list) or (obj is None and key == '0'):

                # Create this key's container, if necessary
                if obj is None:
                    obj = parent[key_parent] = []

                # Parse the key as an integer
                try:
                    key = int(key)
                except:
                    raise ValueError(f"Invalid array index {key!r:.100s} in key {key_str!r:.100s}")

                # Append the value placeholder None
                if key == len(obj):
                    obj.append(None)
                elif key < 0 or key > len(obj):
                    raise ValueError(f"Invalid array index {key} in key {key_str!r:.100s}")

            # Dictionary key
            else:

                # Create this key's container, if necessary
                if obj is None:
                    obj = parent[key_parent] = {}

                # Create the index for this key
                if obj.get(key) is None:
                    obj[key] = None

            # Update the parent object and key
            parent = obj
            key_parent = key

        # Set the value
        if parent[key_parent] is not None:
            raise ValueError(f"Duplicate key {key_str!r:.100s}")
        parent[key_parent] = value

    return result[0] if result[0] is not None else {}
