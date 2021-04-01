// Licensed under the MIT License
// https://github.com/craigahobbs/chisel/blob/master/LICENSE

import {validateTypeModelTypesErrors} from './schemaUtil.js';

/* eslint-disable prefer-template */


// Schema Markdown regex
const RE_PART_ID = '(?:[A-Za-z]\\w*)';
const RE_PART_ATTR_GROUP =
      '(?:(?<nullable>nullable)' +
      '|(?<op><=|<|>|>=|==)\\s*(?<opnum>-?\\d+(?:\\.\\d+)?)' +
      '|(?<ltype>len)\\s*(?<lop><=|<|>|>=|==)\\s*(?<lopnum>\\d+))';
const RE_PART_ATTR = RE_PART_ATTR_GROUP.replace(/\(\?<[^>]+>/g, '(?:');
const RE_PART_ATTRS = '(?:' + RE_PART_ATTR + '(?:\\s*,\\s*' + RE_PART_ATTR + ')*)';
const RE_ATTR_GROUP = new RegExp(RE_PART_ATTR_GROUP);
const RE_FIND_ATTRS = new RegExp(RE_PART_ATTR + '(?:\\s*,\\s*|\\s*$)', 'g');
const RE_LINE_CONT = /\\\s*$/;
const RE_COMMENT = /^\s*(?:#-.*|#(?<doc>.*))?$/;
const RE_GROUP = /^group(?:\s+"(?<group>.+?)")?\s*$/;
const RE_ACTION = new RegExp('^action\\s+(?<id>' + RE_PART_ID + ')');
const RE_PART_BASE_IDS = '(?:\\s*\\(\\s*(?<base_ids>' + RE_PART_ID + '(?:\\s*,\\s*' + RE_PART_ID + ')*)\\s*\\)\\s*)';
const RE_BASE_IDS_SPLIT = /\s*,\s*/;
const RE_DEFINITION = new RegExp('^(?<type>struct|union|enum)\\s+(?<id>' + RE_PART_ID + ')' + RE_PART_BASE_IDS + '?\\s*$');
const RE_SECTION = new RegExp('^\\s+(?<type>path|query|input|output|errors)' + RE_PART_BASE_IDS + '?\\s*$');
const RE_SECTION_PLAIN = /^\s+(?<type>urls)\s*$/;
const RE_PART_TYPEDEF =
      '(?<type>' + RE_PART_ID + ')' +
      '(?:\\s*\\(\\s*(?<attrs>' + RE_PART_ATTRS + ')\\s*\\))?' +
      '(?:' +
      '(?:\\s*\\[\\s*(?<array>' + RE_PART_ATTRS + '?)\\s*\\])?' +
      '|' +
      '(?:' +
      '\\s*:\\s*(?<dictValueType>' + RE_PART_ID + ')' +
      '(?:\\s*\\(\\s*(?<dictValueAttrs>' + RE_PART_ATTRS + ')\\s*\\))?' +
      ')?' +
      '(?:\\s*\\{\\s*(?<dict>' + RE_PART_ATTRS + '?)\\s*\\})?' +
      ')' +
      '\\s+(?<id>' + RE_PART_ID + ')';
const RE_TYPEDEF = new RegExp('^typedef\\s+' + RE_PART_TYPEDEF + '\\s*$');
const RE_MEMBER = new RegExp('^\\s+(?<optional>optional\\s+)?' + RE_PART_TYPEDEF + '\\s*$');
const RE_VALUE = new RegExp('^\\s+(?<id>' + RE_PART_ID + ')\\s*$');
const RE_VALUE_QUOTED = new RegExp('^\\s+"(?<id>' + RE_PART_ID + '.*?)"\\s*$');
const RE_URL = /^\s+(?<method>[A-Za-z]+|\*)(?:\s+(?<path>\/[^\s]*))?/;


// Built-in types
const BUILTIN_TYPES = new Set(['bool', 'date', 'datetime', 'float', 'int', 'object', 'string', 'uuid']);


// Helper function to parse an attributes string - returns an attributes model
function parseAttr(attrsString) {
    let attrs = null;
    if (typeof attrsString !== 'undefined') {
        for (const [attrString] of attrsString.matchAll(RE_FIND_ATTRS)) {
            if (attrs === null) {
                attrs = {};
            }
            const matchAttr = attrString.match(RE_ATTR_GROUP);
            const attrOp = matchAttr.groups.op;
            const attrLengthOp = matchAttr.groups.lop;

            if (typeof matchAttr.groups.nullable !== 'undefined') {
                attrs.nullable = true;
            } else if (typeof attrOp !== 'undefined') {
                const attrValue = parseFloat(matchAttr.groups.opnum);
                if (attrOp === '<') {
                    attrs.lt = attrValue;
                } else if (attrOp === '<=') {
                    attrs.lte = attrValue;
                } else if (attrOp === '>') {
                    attrs.gt = attrValue;
                } else if (attrOp === '>=') {
                    attrs.gte = attrValue;
                } else {
                    attrs.eq = attrValue;
                }
            } else {
                // typeof attrLengthOp !== 'undefined'
                const attrValue = parseInt(matchAttr.groups.lopnum, 10);
                if (attrLengthOp === '<') {
                    attrs.lenLT = attrValue;
                } else if (attrLengthOp === '<=') {
                    attrs.lenLTE = attrValue;
                } else if (attrLengthOp === '>') {
                    attrs.lenGT = attrValue;
                } else if (attrLengthOp === '>=') {
                    attrs.lenGTE = attrValue;
                } else {
                    attrs.lenEq = attrValue;
                }
            }
        }
    }
    return attrs;
}


// Helper function to create a type model
function createType(typeName) {
    if (BUILTIN_TYPES.has(typeName)) {
        return {'builtin': typeName};
    }
    return {'user': typeName};
}


// Helper function to parse a typedef - returns a type-model and attributes-model tuple
function parseTypedef(matchTypedef) {
    const arrayAttrsString = matchTypedef.groups.array;
    const dictAttrsString = matchTypedef.groups.dict;

    // Array type?
    if (typeof arrayAttrsString !== 'undefined') {
        const valueTypeName = matchTypedef.groups.type;
        const valueAttr = parseAttr(matchTypedef.groups.attrs);
        const arrayType = {'type': createType(valueTypeName)};
        if (valueAttr !== null) {
            arrayType.attr = valueAttr;
        }
        return [{'array': arrayType}, parseAttr(arrayAttrsString)];
    }

    // Dictionary type?
    if (typeof dictAttrsString !== 'undefined') {
        let dictType;
        let valueTypeName = matchTypedef.groups.dictValueType;
        if (typeof valueTypeName !== 'undefined') {
            const valueAttr = parseAttr(matchTypedef.groups.dictValueAttrs);
            const keyTypeName = matchTypedef.groups.type;
            const keyAttr = parseAttr(matchTypedef.groups.attrs);
            dictType = {
                'type': createType(valueTypeName),
                'keyType': createType(keyTypeName)
            };
            if (valueAttr !== null) {
                dictType.attr = valueAttr;
            }
            if (keyAttr !== null) {
                dictType.keyAttr = keyAttr;
            }
        } else {
            valueTypeName = matchTypedef.groups.type;
            const valueAttr = parseAttr(matchTypedef.groups.attrs);
            dictType = {'type': createType(valueTypeName)};
            if (valueAttr !== null) {
                dictType.attr = valueAttr;
            }
        }
        return [{'dict': dictType}, parseAttr(dictAttrsString)];
    }

    // Non-container type...
    const memberTypeName = matchTypedef.groups.type;
    return [createType(memberTypeName), parseAttr(matchTypedef.groups.attrs)];
}


// Helper function to compare tuples/lists
const compareTuple =
      (v1, v2) => (v1.reduce((tot, val, idx) => (tot !== 0 ? tot : (val < v2[idx] ? -1 : (val > v2[idx] ? 1 : 0))), 0));


/**
 * Schema Markdown parser exception
 *
 * @property {string[]} errors - The list of error strings
 */
class SchemaMarkdownParserError extends Error {
    /**
     * Create a Schema Markdown parser error instance
     *
     * @param {string[]} errors - The list of error strings
     */
    constructor(errors) {
        super(errors.join('\n'));
        this.errors = errors;
    }
}


/**
 * The parser class for Schema Markdown. Parsing can occur at initialization time or by calling the
 * "parseString" method, which can be called repeatedly.
 *
 * @property {Object} types - The map of user type name to user type model
 * @property {Object} errorMap - Set of filename, linenum, and error-message tuples
 * @property {Object} filepos - Map of definition-name to filename/linenum-tuples
 */
export class SchemaMarkdownParser {
    /**
     * Create a Schema Markdown parser instance
     *
     * @param {string} [text=null]: An optional Schema Markdown string to parse
     * @param {Object} [types=null]: An optional map of user type name to user type model
     * @throws {SchemaMarkdownParserError}
     */
    constructor(text = null, types = null) {
        this.types = types !== null ? types : {};
        this.errorMap = {};
        this.filepos = {};

        // Parse the Schema Markdown string, if any
        if (text !== null) {
            this.parseString(text);
        }
    }

    addError(msg, filename, linenum) {
        const errorMsg = `${filename}:${linenum}: error: ${msg}`;
        this.errorMap[errorMsg] = [filename, linenum, errorMsg];
    }

    getFilepos(typeName, typeKey) {
        let filepos = null;
        if (typeKey !== null) {
            const key = `${typeName}.${typeKey}`;
            filepos = key in this.filepos ? this.filepos[key] : null;
        }
        if (filepos === null) {
            filepos = typeName in this.filepos ? this.filepos[typeName] : null;
        }
        if (filepos === null) {
            filepos = ['', 1];
        }
        return filepos;
    }

    /**
     * The list of parser error strings
     */
    get errors() {
        return Array.from(Object.values(this.errorMap)).sort(compareTuple).map(([,, msg]) => msg);
    }

    /**
     * Finalize a parsing operation. You only need to call this method if you set the "parse"
     * method's "finalize" argument to false.
     *
     * @throws {SchemaMarkdownParserError}
     */
    finalize() {
        // Do the finalization
        for (const [typeName, memberName, errorMsg] of validateTypeModelTypesErrors(this.types)) {
            this.addError(errorMsg, ...this.getFilepos(typeName, memberName));
        }

        // Raise a parser exception if there are any errors
        const {errors} = this;
        if (errors.length) {
            throw new SchemaMarkdownParserError(errors);
        }
    }

    /**
     * Parse a Schema Markdown string. This method can be called repeatedly.
     *
     * @param {string} text - The Schema Markdown string
     * @param {string} [filename=''] - The name of file being parsed (for error messages)
     * @param {boolean} [finalize=true] - If true, resolve names after parsing. Be sure to call the
     *     "finalize" method when finished.
     * @throws {SchemaMarkdownParserError}
     */
    parseString(text, filename = '', finalize = true) {
        this.parse(text.split(/\r?\n/), filename, finalize);
    }

    /**
     * Parse Schema Markdown from an iterator of line strings (e.g an input stream). This method can
     * be called repeatedly.
     *
     * @param {string[]} lines - An array of Schema Markdown line strings
     * @param {string} [filename=''] - The name of file being parsed (for error messages)
     * @param {boolean} [finalize=true] - If true, resolve names after parsing. Be sure to call the
     *     "finalize" method when finished.
     * @throws {SchemaMarkdownParserError}
     */
    parse(lines, filename = '', finalize = true) {
        // Current parser state
        let action = null;
        let urls = null;
        let userType = null;
        let doc = [];
        let docGroup = null;
        let linenum = 0;

        // Helper function to get documentation strings
        const getDoc = () => {
            let result = null;
            if (doc.length) {
                result = doc;
                doc = [];
            }
            return result;
        };

        // Process each line
        const lineContinuation = [];
        const lineGroups = [lines, ['']];
        for (const lineGroup of lineGroups) {
            for (const linePart of lineGroup) {
                linenum += 1;

                // Line continuation?
                const linePartNoContinuation = linePart.replace(RE_LINE_CONT, '');
                if (lineContinuation.length || linePartNoContinuation !== linePart) {
                    lineContinuation.push(linePartNoContinuation);
                }
                if (linePartNoContinuation !== linePart) {
                    continue;
                }
                let line;
                if (lineContinuation.length) {
                    line = lineContinuation.join('');
                    lineContinuation.length = 0;
                } else {
                    line = linePart;
                }

                // Match syntax
                let [matchName, match] = ['comment', line.match(RE_COMMENT)];
                if (match === null) {
                    [matchName, match] = ['group', line.match(RE_GROUP)];
                }
                if (match === null) {
                    [matchName, match] = ['action', line.match(RE_ACTION)];
                }
                if (match === null) {
                    [matchName, match] = ['definition', line.match(RE_DEFINITION)];
                }
                if (match === null && action !== null) {
                    [matchName, match] = ['section', line.match(RE_SECTION)];
                }
                if (match === null && action !== null) {
                    [matchName, match] = ['section_plain', line.match(RE_SECTION_PLAIN)];
                }
                if (match === null && userType !== null && 'enum' in userType) {
                    const matchValue = line.match(RE_VALUE);
                    if (matchValue !== null) {
                        [matchName, match] = ['value', matchValue];
                    } else {
                        [matchName, match] = ['value', line.match(RE_VALUE_QUOTED)];
                    }
                }
                if (match === null && userType !== null && 'struct' in userType) {
                    [matchName, match] = ['member', line.match(RE_MEMBER)];
                }
                if (match === null && urls !== null) {
                    [matchName, match] = ['urls', line.match(RE_URL)];
                }
                if (match === null) {
                    [matchName, match] = ['typedef', line.match(RE_TYPEDEF)];
                }
                if (match === null) {
                    matchName = null;
                }

                // Comment?
                if (matchName === 'comment') {
                    const docString = match.groups.doc;
                    if (typeof docString !== 'undefined') {
                        doc.push(!docString.startsWith(' ') ? docString : docString.slice(1));
                    }

                // Documentation group?
                } else if (matchName === 'group') {
                    docGroup = match.groups.group;
                    if (typeof docGroup !== 'undefined') {
                        docGroup = docGroup.trim();
                    } else {
                        docGroup = null;
                    }

                // Action?
                } else if (matchName === 'action') {
                    const actionId = match.groups.id;

                    // Action already defined?
                    if (actionId in this.types) {
                        this.addError(`Redefinition of action '${actionId}'`, filename, linenum);
                    }

                    // Clear parser state
                    urls = null;
                    userType = null;
                    const actionDoc = getDoc();

                    // Create the new action
                    action = {'name': actionId};
                    this.types[actionId] = {'action': action};
                    if (actionDoc !== null) {
                        action.doc = actionDoc;
                    }
                    if (docGroup !== null) {
                        action.docGroup = docGroup;
                    }

                // Definition?
                } else if (matchName === 'definition') {
                    const definitionString = match.groups.type;
                    const definitionId = match.groups.id;
                    const definitionBaseIds = match.groups.base_ids;

                    // Type already defined?
                    if (BUILTIN_TYPES.has(definitionId) || definitionId in this.types) {
                        this.addError(`Redefinition of type '${definitionId}'`, filename, linenum);
                    }

                    // Clear parser state
                    action = null;
                    urls = null;
                    const definitionDoc = getDoc();

                    // Struct definition
                    if (definitionString === 'struct' || definitionString === 'union') {
                        // Create the new struct type
                        const struct = {'name': definitionId};
                        userType = {'struct': struct};
                        this.types[definitionId] = userType;
                        if (definitionDoc !== null) {
                            struct.doc = definitionDoc;
                        }
                        if (docGroup !== null) {
                            struct.docGroup = docGroup;
                        }
                        if (definitionString === 'union') {
                            struct.union = true;
                        }
                        if (typeof definitionBaseIds !== 'undefined') {
                            struct.bases = definitionBaseIds.split(RE_BASE_IDS_SPLIT);
                        }

                    // Enum definition
                    } else {
                        // definition_string == 'enum':
                        // Create the new enum type
                        const enum_ = {'name': definitionId};
                        userType = {'enum': enum_};
                        this.types[definitionId] = userType;
                        if (definitionDoc !== null) {
                            enum_.doc = definitionDoc;
                        }
                        if (docGroup !== null) {
                            enum_.docGroup = docGroup;
                        }
                        if (typeof definitionBaseIds !== 'undefined') {
                            enum_.bases = definitionBaseIds.split(RE_BASE_IDS_SPLIT);
                        }
                    }

                    // Record finalization information
                    this.filepos[definitionId] = [filename, linenum];

                // Action section?
                } else if (matchName === 'section') {
                    const sectionString = match.groups.type;
                    const sectionBaseIds = match.groups.base_ids;

                    // Action section redefinition?
                    if (sectionString in action) {
                        this.addError(`Redefinition of action ${sectionString}`, filename, linenum);
                    }

                    // Clear parser state
                    urls = null;

                    // Set the action section type
                    const sectionTypeName = `${action.name}_${sectionString}`;
                    action[sectionString] = sectionTypeName;
                    if (sectionString === 'errors') {
                        const enum_ = {'name': sectionTypeName};
                        userType = {'enum': enum_};
                        this.types[sectionTypeName] = userType;
                        if (typeof sectionBaseIds !== 'undefined') {
                            enum_.bases = sectionBaseIds.split(RE_BASE_IDS_SPLIT);
                        }
                    } else {
                        const struct = {'name': sectionTypeName};
                        userType = {'struct': struct};
                        this.types[sectionTypeName] = userType;
                        if (typeof sectionBaseIds !== 'undefined') {
                            struct.bases = sectionBaseIds.split(RE_BASE_IDS_SPLIT);
                        }
                    }

                    // Record finalization information
                    this.filepos[sectionTypeName] = [filename, linenum];

                // Plain action section?
                } else if (matchName === 'section_plain') {
                    const sectionString = match.groups.type;

                    // Action section redefinition?
                    if (sectionString in action) {
                        this.addError(`Redefinition of action ${sectionString}`, filename, linenum);
                    }

                    // Clear parser state
                    userType = null;

                    // Update the parser state
                    urls = [];

                // Enum value?
                } else if (matchName === 'value') {
                    const valueString = match.groups.id;

                    // Add the enum value
                    const enum_ = userType.enum;
                    if (!('values' in enum_)) {
                        enum_.values = [];
                    }
                    const enumValue = {'name': valueString};
                    enum_.values.push(enumValue);
                    const enumValueDoc = getDoc();
                    if (enumValueDoc !== null) {
                        enumValue.doc = enumValueDoc;
                    }

                    // Record finalization information
                    this.filepos[`${enum_.name}.${valueString}`] = [filename, linenum];

                // Struct member?
                } else if (matchName === 'member') {
                    const optional = typeof match.groups.optional !== 'undefined';
                    const memberName = match.groups.id;

                    // Add the member
                    const {struct} = userType;
                    if (!('members' in struct)) {
                        struct.members = [];
                    }
                    const [memberType, memberAttr] = parseTypedef(match);
                    const memberDoc = getDoc();
                    const member = {
                        'name': memberName,
                        'type': memberType
                    };
                    struct.members.push(member);
                    if (memberAttr !== null) {
                        member.attr = memberAttr;
                    }
                    if (memberDoc !== null) {
                        member.doc = memberDoc;
                    }
                    if (optional) {
                        member.optional = true;
                    }

                    // Record finalization information
                    this.filepos[`${struct.name}.${memberName}`] = [filename, linenum];

                // URL?
                } else if (matchName === 'urls') {
                    const {method, path} = match.groups;

                    // Create the action URL object
                    const actionUrl = {};
                    if (method !== '*') {
                        actionUrl.method = method;
                    }
                    if (typeof path !== 'undefined') {
                        actionUrl.path = path;
                    }

                    // Duplicate URL?
                    if (urls.some((url) => url.method === actionUrl.method && url.path === actionUrl.path)) {
                        this.addError(`Duplicate URL: ${method} ${'path' in actionUrl ? actionUrl.path : ''}`, filename, linenum);
                    }

                    // Add the URL
                    if (!('urls' in action)) {
                        action.urls = urls;
                    }
                    urls.push(actionUrl);

                // Typedef?
                } else if (matchName === 'typedef') {
                    const definitionId = match.groups.id;

                    // Type already defined?
                    if (BUILTIN_TYPES.has(definitionId) || definitionId in this.types) {
                        this.addError(`Redefinition of type '${definitionId}'`, filename, linenum);
                    }

                    // Clear parser state
                    action = null;
                    urls = null;
                    userType = null;
                    const typedefDoc = getDoc();

                    // Create the typedef
                    const [typedefType, typedefAttr] = parseTypedef(match);
                    const typedef = {
                        'name': definitionId,
                        'type': typedefType
                    };
                    this.types[definitionId] = {'typedef': typedef};
                    if (typedefAttr !== null) {
                        typedef.attr = typedefAttr;
                    }
                    if (typedefDoc !== null) {
                        typedef.doc = typedefDoc;
                    }
                    if (docGroup !== null) {
                        typedef.docGroup = docGroup;
                    }

                    // Record finalization information
                    this.filepos[definitionId] = [filename, linenum];

                // Unrecognized line syntax
                } else {
                    this.addError('Syntax error', filename, linenum);
                }
            }
        }

        // Finalize, if requested
        if (finalize) {
            this.finalize();
        }
    }
}
