// Licensed under the MIT License
// https://github.com/craigahobbs/schema-markdown/blob/master/LICENSE

import {encodeParams, nbsp} from './util.js';
import {getEnumValues, getReferencedTypes, getStructMembers} from './schema.js';
import {markdownElements, markdownParse} from './markdown.js';


/**
 * Generate a user type's element model
 *
 * @property {Object} [params = {}] - The page's hash params
 */
export class UserTypeElements {
    /**
     * Create a user-type-element-model object
     *
     * @param {Object} [params = {}] - The page's hash params
     */
    constructor(params = {}) {
        this.params = params;
    }

    /**
     * Generate the user type's element model
     *
     * @param {Object} types - The map of user type name to user type model
     * @param {string} typeName - The type name
     * @param {string[]} actionUrls - For action types, the action URL override
     * @returns {Object[]}
     */
    getElements(types, typeName, actionUrls = null) {
        // Compute the referenced types
        const userType = types[typeName];
        const action = 'action' in userType ? userType.action : null;
        const referencedTypes = getReferencedTypes(types, typeName);
        let typesFilter;
        if (action !== null) {
            typesFilter = [typeName, action.path, action.query, action.input, action.output, action.errors];
        } else {
            typesFilter = [typeName];
        }
        const filteredTypes =
              Object.entries(referencedTypes).sort().filter(([name]) => !typesFilter.includes(name)).map(([, type]) => type);

        // Return the user type's element model
        return [
            // The user type
            this.userTypeElem(types, typeName, actionUrls, 'h1', typeName),

            // Referenced types
            !filteredTypes.length ? null : [
                {'html': 'hr'},
                {'html': 'h2', 'elem': {'text': 'Referenced Types'}},
                filteredTypes.map((refType) => this.userTypeElem(types, Object.values(refType)[0].name, null, 'h3'))
            ]
        ];
    }

    /**
     * Generate an action's URL note element model
     *
     * @param {?Object[]} [urls=null] - The array of request URL models or null
     * @returns {Object}
     */
    static getUrlNoteElements(urls) {
        return urls === null || !urls.length ? null : {'html': 'p', 'attr': {'class': 'smd-note'}, 'elem': [
            {'html': 'b', 'elem': {'text': 'Note: '}},
            {'text': `The request is exposed at the following ${urls.length > 1 ? 'URLs:' : 'URL:'}`},
            {'html': 'ul', 'elem': urls.map((url) => ({'html': 'li', 'elem': [
                {'html': 'a', 'attr': {'href': url.url}, 'elem': {'text': url.method ? `${url.method} ${url.url}` : url.url}}
            ]}))}
        ]};
    }

    /**
     * Helper function to generate markdown text's element model
     *
     * @param {?string} [text=null] - The markdown text
     * @returns {Array}
     */
    static markdownElem(text = null) {
        if (text === null) {
            return null;
        }
        return markdownElements(markdownParse(text));
    }

    // Helper method to get a user type href (target)
    typeHref(typeName) {
        return `${encodeParams(this.params)}&type_${typeName}`;
    }

    // Helper method to generate a member/typedef type's element model
    typeElem(type) {
        if ('array' in type) {
            return [this.typeElem(type.array.type), {'text': `${nbsp}[]`}];
        } else if ('dict' in type) {
            return [
                !('keyType' in type.dict) || 'builtin' in type.dict.keyType ? null
                    : [this.typeElem(type.dict.keyType), {'text': `${nbsp}:${nbsp}`}],
                this.typeElem(type.dict.type),
                {'text': `${nbsp}{}`}
            ];
        } else if ('user' in type) {
            return {'html': 'a', 'attr': {'href': `#${this.typeHref(type.user)}`}, 'elem': {'text': type.user}};
        }
        return {'text': type.builtin};
    }

    // Helper method to generate a member/typedef's attributes element model
    static attrElem({type, attr = null, optional = false}) {
        // Create the array of attribute "parts" (lhs, op, rhs)
        const parts = [];
        const typeName = type.array ? 'array' : (type.dict ? 'dict' : 'value');
        UserTypeElements.attrParts(parts, typeName, attr, optional);

        // Array or dict key/value attributes?
        if ('array' in type) {
            if ('attr' in type.array) {
                UserTypeElements.attrParts(parts, 'value', type.array.attr, false);
            }
        } else if ('dict' in type) {
            if ('keyAttr' in type.dict) {
                UserTypeElements.attrParts(parts, 'key', type.dict.keyAttr, false);
            }
            if ('attr' in type.dict) {
                UserTypeElements.attrParts(parts, 'value', type.dict.attr, false);
            }
        }

        // Return the attributes element model
        return !parts.length ? null : {'html': 'ul', 'attr': {'class': 'smd-attr-list'}, 'elem': parts.map(
            (part) => ({
                'html': 'li',
                'elem': {'text': part.op ? `${part.lhs}${nbsp}${part.op}${nbsp}${part.rhs}` : part.lhs}
            })
        )};
    }

    // Helper method for attrElem to generate a type's attribute "parts"
    static attrParts(parts, noun, attr, optional) {
        if (optional) {
            parts.push({'lhs': 'optional'});
        }
        if (attr !== null && 'nullable' in attr) {
            parts.push({'lhs': 'nullable'});
        }
        if (attr !== null && 'gt' in attr) {
            parts.push({'lhs': noun, 'op': '>', 'rhs': attr.gt});
        }
        if (attr !== null && 'gte' in attr) {
            parts.push({'lhs': noun, 'op': '>=', 'rhs': attr.gte});
        }
        if (attr !== null && 'lt' in attr) {
            parts.push({'lhs': noun, 'op': '<', 'rhs': attr.lt});
        }
        if (attr !== null && 'lte' in attr) {
            parts.push({'lhs': noun, 'op': '<=', 'rhs': attr.lte});
        }
        if (attr !== null && 'eq' in attr) {
            parts.push({'lhs': noun, 'op': '==', 'rhs': attr.eq});
        }
        if (attr !== null && 'lenGT' in attr) {
            parts.push({'lhs': `len(${noun})`, 'op': '>', 'rhs': attr.lenGT});
        }
        if (attr !== null && 'lenGTE' in attr) {
            parts.push({'lhs': `len(${noun})`, 'op': '>=', 'rhs': attr.lenGTE});
        }
        if (attr !== null && 'lenLT' in attr) {
            parts.push({'lhs': `len(${noun})`, 'op': '<', 'rhs': attr.lenLT});
        }
        if (attr !== null && 'lenLTE' in attr) {
            parts.push({'lhs': `len(${noun})`, 'op': '<=', 'rhs': attr.lenLTE});
        }
        if (attr !== null && 'lenEq' in attr) {
            parts.push({'lhs': `len(${noun})`, 'op': '==', 'rhs': attr.lenEq});
        }
    }

    // Helper method to generate a user type's element model
    userTypeElem(types, typeName, urls, titleTag, title = null, introMarkdown = null) {
        const userType = types[typeName];

        // Generate the header element models
        const titleElem = (titleDefault) => ({
            'html': titleTag,
            'attr': {'id': this.typeHref(typeName)},
            'elem': {'html': 'a', 'attr': {'class': 'linktarget'}, 'elem': {'text': title !== null ? title : titleDefault}}
        });

        // Struct?
        if ('struct' in userType) {
            const {struct} = userType;
            const members = 'members' in struct ? getStructMembers(types, struct) : null;
            const memberAttrElem = members !== null
                ? Object.fromEntries(members.map((member) => [member.name, UserTypeElements.attrElem(member)])) : null;
            const hasAttr = members !== null && Object.values(memberAttrElem).some((attrElem) => attrElem !== null);
            const memberDocElem = members !== null
                ? Object.fromEntries(members.map(({name, doc}) => [name, UserTypeElements.markdownElem(doc)])) : null;
            const hasDoc = members !== null && Object.values(memberDocElem).some((docElem) => docElem !== null);

            // Return the struct documentation element model
            return [
                titleElem('union' in struct && struct.union ? `union ${typeName}` : `struct ${typeName}`),
                UserTypeElements.markdownElem(struct.doc),

                // Struct members
                !members || !members.length ? UserTypeElements.markdownElem('The struct is empty.') : {'html': 'table', 'elem': [
                    {'html': 'tr', 'elem': [
                        {'html': 'th', 'elem': {'text': 'Name'}},
                        {'html': 'th', 'elem': {'text': 'Type'}},
                        hasAttr ? {'html': 'th', 'elem': {'text': 'Attributes'}} : null,
                        hasDoc ? {'html': 'th', 'elem': {'text': 'Description'}} : null
                    ]},
                    members.map((member) => ({'html': 'tr', 'elem': [
                        {'html': 'td', 'elem': {'text': member.name}},
                        {'html': 'td', 'elem': this.typeElem(member.type)},
                        hasAttr ? {'html': 'td', 'elem': memberAttrElem[member.name]} : null,
                        hasDoc ? {'html': 'td', 'elem': memberDocElem[member.name]} : null
                    ]}))
                ]}
            ];

        // Enumeration?
        } else if ('enum' in userType) {
            const enum_ = userType.enum;
            const values = 'values' in enum_ ? getEnumValues(types, enum_) : null;
            const valueDocElem = values !== null
                ? Object.fromEntries(values.map(({name, doc}) => [name, UserTypeElements.markdownElem(doc)])) : null;
            const hasDoc = values !== null && Object.values(valueDocElem).some((docElem) => docElem !== null);

            // Return the enumeration documentation element model
            return [
                titleElem(`enum ${typeName}`),
                UserTypeElements.markdownElem(enum_.doc),
                introMarkdown !== null ? UserTypeElements.markdownElem(introMarkdown) : null,

                // Enumeration values
                !values || !values.length ? UserTypeElements.markdownElem('The enum is empty.') : {'html': 'table', 'elem': [
                    {'html': 'tr', 'elem': [
                        {'html': 'th', 'elem': {'text': 'Value'}},
                        hasDoc ? {'html': 'th', 'elem': {'text': 'Description'}} : null
                    ]},
                    values.map((value) => ({'html': 'tr', 'elem': [
                        {'html': 'td', 'elem': {'text': value.name}},
                        hasDoc ? {'html': 'td', 'elem': valueDocElem[value.name]} : null
                    ]}))
                ]}
            ];

        // Typedef?
        } else if ('typedef' in userType) {
            const {typedef} = userType;
            const attrElem = 'attr' in typedef ? UserTypeElements.attrElem(typedef) : null;

            // Return the typedef documentation element model
            return [
                titleElem(`typedef ${typeName}`),
                UserTypeElements.markdownElem(typedef.doc),

                // Typedef type description
                {'html': 'table', 'elem': [
                    {'html': 'tr', 'elem': [
                        {'html': 'th', 'elem': {'text': 'Type'}},
                        attrElem !== null ? {'html': 'th', 'elem': {'text': 'Attributes'}} : null
                    ]},
                    {'html': 'tr', 'elem': [
                        {'html': 'td', 'elem': this.typeElem(typedef.type)},
                        attrElem !== null ? {'html': 'td', 'elem': attrElem} : null
                    ]}
                ]}
            ];

        // Action?
        } else if ('action' in userType) {
            const {action} = userType;

            // Add "UnexpectedError" to the action's errors
            const actionErrorTypeName = `${action.name}_errors`;
            const actionErrorValues = 'errors' in action && 'enum' in types[action.errors] ? types[action.errors].enum.values : [];
            const actionErrorTypes = {};
            actionErrorTypes[actionErrorTypeName] = {
                'enum': {
                    'name': actionErrorTypeName,
                    'values': [
                        {
                            'name': 'UnexpectedError',
                            'doc': ['An unexpected error occurred while processing the request']
                        },
                        ...actionErrorValues
                    ]
                }
            };

            // If no URLs passed use the action's URLs
            let actionUrls = urls;
            if (urls === null && 'urls' in action) {
                actionUrls = action.urls.map(({method = null, path = null}) => {
                    const url = {
                        'url': path !== null ? path : `/${typeName}`
                    };
                    if (method !== null) {
                        url.method = method;
                    }
                    return url;
                });
            }

            // Return the action documentation element model
            return [
                titleElem(`action ${typeName}`),
                UserTypeElements.markdownElem(action.doc),
                UserTypeElements.getUrlNoteElements(actionUrls),

                // Action types
                'path' in action ? this.userTypeElem(types, action.path, null, 'h2', 'Path Parameters') : null,
                'query' in action ? this.userTypeElem(types, action.query, null, 'h2', 'Query Parameters') : null,
                'input' in action ? this.userTypeElem(types, action.input, null, 'h2', 'Input Parameters') : null,
                'output' in action ? this.userTypeElem(types, action.output, null, 'h2', 'Output Parameters') : null,
                this.userTypeElem(
                    actionErrorTypes,
                    actionErrorTypeName,
                    null,
                    'h2',
                    'Error Codes',
                    `\
If an application error occurs, the response is of the form:

    {
        "error": "<code>",
        "message": "<message>"
    }

"message" is optional. "<code>" is one of the following values:`
                )
            ];
        }

        // Unreachable for valid type models
        return null;
    }
}
