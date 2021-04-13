# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/main/LICENSE

"""
The schema-markdown type model definition
"""

from .parser import SchemaMarkdownParser


#: The Schema Markdown type model defined as Schema Markdown.
TYPE_MODEL_SMD = '''\
# A type model with a title
struct TypeModel

    # The type model's title
    string title

    # The type model
    Types types


# Map of user type name to user type model
typedef UserType{len > 0} Types


# Union representing a member type
union Type

    # A built-in type
    BuiltinType builtin

    # An array type
    Array array

    # A dictionary type
    Dict dict

    # A user type name
    string user


# A type or member's attributes
struct Attributes

    # If true, the value may be null
    optional bool nullable

    # The value is equal
    optional float eq

    # The value is less than
    optional float lt

    # The value is less than or equal to
    optional float lte

    # The value is greater than
    optional float gt

    # The value is greater than or equal to
    optional float gte

    # The length is equal to
    optional int lenEq

    # The length is less-than
    optional int lenLT

    # The length is less than or equal to
    optional int lenLTE

    # The length is greater than
    optional int lenGT

    # The length is greater than or equal to
    optional int lenGTE


# The built-in type enumeration
enum BuiltinType

    # The string type
    string

    # The integer type
    int

    # The float type
    float

    # The boolean type
    bool

    # A date formatted as an ISO-8601 date string
    date

    # A date/time formatted as an ISO-8601 date/time string
    datetime

    # A UUID formatted as string
    uuid

    # An object of any type
    object


# An array type
struct Array

    # The contained type
    Type type

    # The contained type's attributes
    optional Attributes attr


# A dictionary type
struct Dict

    # The contained key type
    Type type

    # The contained key type's attributes
    optional Attributes attr

    # The contained value type
    optional Type keyType

    # The contained value type's attributes
    optional Attributes keyAttr


# A user type
union UserType

    # An enumeration type
    Enum enum

    # A struct type
    Struct struct

    # A type definition
    Typedef typedef

    # A JSON web API (not reference-able)
    Action action


# User type base struct
struct UserBase

    # The user type name
    string name

    # The documentation markdown text lines
    optional string[] doc

    # The documentation group name
    optional string docGroup


# An enumeration type
struct Enum (UserBase)

    # The enum's base enumerations
    optional string[len > 0] bases

    # The enumeration values
    optional EnumValue[len > 0] values


# An enumeration type value
struct EnumValue

    # The value string
    string name

    # The documentation markdown text lines
    optional string[] doc


# A struct type
struct Struct (UserBase)

    # The struct's base classes
    optional string[len > 0] bases

    # If true, the struct is a union and exactly one of the optional members is present
    optional bool union

    # The struct members
    optional StructMember[len > 0] members


# A struct member
struct StructMember

    # The member name
    string name

    # The documentation markdown text lines
    optional string[] doc

    # The member type
    Type type

    # The member type attributes
    optional Attributes attr

    # If true, the member is optional and may not be present
    optional bool optional


# A typedef type
struct Typedef (UserBase)

    # The typedef's type
    Type type

    # The typedef's type attributes
    optional Attributes attr


# A JSON web service API
struct Action (UserBase)

    # The action's URLs
    optional ActionURL[len > 0] urls

    # The path parameters struct type name
    optional string path

    # The query parameters struct type name
    optional string query

    # The content body struct type name
    optional string input

    # The response body struct type name
    optional string output

    # The custom error response codes enum type name
    optional string errors


# An action URL model
struct ActionURL

    # The HTTP method. If not provided, matches all HTTP methods.
    optional string method

    # The URL path. If not provided, uses the default URL path of "/<actionName>".
    optional string path
'''


#: The Schema Markdown type model.
TYPE_MODEL = {
    'title': 'The Schema Markdown Type Model',
    'types': SchemaMarkdownParser(TYPE_MODEL_SMD).types
}
